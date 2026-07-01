import logging
import json
import asyncio
from typing import Set, Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
import time

from backend.api.models import (
    AudioChunk, CoachMessage, CallMetrics, Suggestion
)
from backend.services.whisper_service import import WhisperService
from backend.services.deepseek_service import DeepSeekService
from backend.services.knowledge_base import KnowledgeBaseService

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests: Dict[str, list] = defaultdict(list)
    
    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests
        client_requests = [req_time for req_time in client_requests 
                          if now - req_time < self.window]
        self.requests[client_id] = client_requests
        
        if len(client_requests) >= self.max_requests:
            return False
        
        client_requests.append(now)
        return True

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metrics: Dict[str, CallMetrics] = defaultdict(CallMetrics)
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client connected: {client_id}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client disconnected: {client_id}")
    
    async def send_message(self, client_id: str, message: CoachMessage):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(
                    message.dict()
                )
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

class WebSocketHandler:
    def __init__(self):
        self.manager = ConnectionManager()
        self.rate_limiter = RateLimiter()
        self.whisper_service = = WhisperService()
        self.deepseek_service = DeepSeekService()
        self.kb_service = KnowledgeBaseService()
        
        # Store conversation context
        self.conversation_context: Dict[str, dict] = defaultdict(dict)
    
    async def handle_connection(self, websocket: WebSocket, client_id: str):
        await self.manager.connect(websocket, client_id)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Validate origin
                origin = websocket.headers.get("origin", "")
                if not self._validate_origin(origin):
                    await self.manager.send_message(client_id, CoachMessage(
                        type="error",
                        data={"message": "Invalid origin"}
                    ))
                    continue
                
                # Rate limiting check
                if not self.rate_limiter.check_rate_limit(client_id):
                    await self.manager.send_message(client_id, CoachMessage(
                        type="error",
                        data={"message": "Rate limit exceeded"}
                    ))
                    continue
                
                # Process based on message type
                if message.get("type") == "audio_chunk":
                    await self._process_audio_chunk(client_id, message)
                elif message.get("type") == "search_kb":
                    await self._process_kb_search(client_id, message)
                elif message.get("type") == "get_metrics":
                    await self._send_metrics(client_id)
                    
        except WebSocketDisconnect:
            self.manager.disconnect(client_id)
        except Exception as e:
            logger.error(f"WebSocket error for {client_id}: {e}")
            self.manager.disconnect(client_id)
    
    async def _process_audio_chunk(self, client_id: str, message: dict):
        """Process incoming audio chunk"""
        try:
            chunk = AudioChunk(**message.get("data", {}))
            
            # Step 1: Transcribe audio
            transcription = await self.whisper_service.transcribe_audio(chunk.data)
            
            # Send transcription result
            await self.manager.send_message(client_id, CoachMessage(
                type="transcription",
                data={
                    "text": transcription["text"],
                    "confidence": transcription["confidence"],
                    "timestamp": chunk.timestamp

                }
            ))
            
            # Step 2: Analyze with DeepSeek (if we have text)
            if transcription["text"].strip():
                context = self.conversation_context.get(client_id, {})
                analysis = await self.deepseek_service.analyze_transcription(
                    transcription["text"],
                    context
                )
                
                # Update context
                self.conversation_context[client_id] = {
                    "last_text": transcription["text"],
                    "sentiment": analysis.sentiment,
                    "intent": analysis.intent,
                    "previous_suggestions": [
                        s.text for s in analysis.suggestions
                    ]
                }
                
                # Send suggestions
                for suggestion in analysis.suggestions:
                    await self.manager.send_message(client_id, CoachMessage(
                        type="suggestion",
                        data={
                            "text": suggestion.text,
                            "priority": suggestion.priority.value,
                            "category": suggestion.category,
                            "timestamp": time.time()
                        }
                    ))
                
                # Update metrics
                metrics = self.manager.connection_metrics[client_id]
                metrics.sentiment_score = analysis.sentiment
                metrics.active_suggestions = len(analysis.suggestions)
                
                # Send metrics update
                await self._send_metrics(client_id)
                
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            await self.manager.send_message(client_id, CoachMessage(
                type="error",
                data={"message": f"Processing error: {str(e)}"}
            ))
    
    async def _process_kb_search(self, client_id: str, message: dict):
        """Process knowledge base search"""
        try:
            query = message.get("data", {}).get("query", "")
            results = self.kb_service.search(query)
            
            await self.manager.send_message(client_id, CoachMessage(
                type="kb_results",
                data={
                    "query": query,
                    "results": [
                        {
                            "title": entry.title,
                            "content": entry.content[:200] + "...",
                            "category": entry.category,
                            "tags": entry.tags
                        }
                        for entry in results
                    ]
                }
            ))
        except Exception as e:
            logger.error(f"KB search error: {e}")
    
    async def _send_metrics(self, client_id: str):
        """Send current metrics to client"""
        metrics = self.manager.connection_metrics.get(client_id, CallMetrics())
        
        await self.manager.send_message(client_id, CoachMessage(
            type="metrics",
            data=metrics.dict()
        ))
    
    def _validate_origin(self, origin: str) -> bool:
        """Validate WebSocket origin"""
        allowed_origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://localhost:5173"
        ]
        return origin in allowed_origins
