import logging
import os
from contextlib import asyncconontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import uuid

from backend.config import config
from backend.api.websocket_handler import WebSocketHandler
from backend.services.knowledge_base import KnowledgeBaseService



# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global instances
ws_handler: Optional[WebSocketHandler] = None
kb_service: Optional[KnowledgeBaseService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ws_handler, kb_service
    
    # Startup
    logger.info("Starting Real-Time Call Coach API")
    
    # Initialize services
    ws_handler = WebSocketHandler()
    kb_service = KnowledgeBaseService()
    
    # Create KB directory if not exists
    os.makedirs(config.KB_DIRECTORY, exist_ok=True)
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    
    logger.info("Services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Real-Time Call Coach API")

# Create FastAPI app
app = FastAPI(
    title="Real-Time Call Coach API",
    description="AI-powered call center coaching system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Skip rate limiting for WebSocket connections
    if request.url.path.startswith("/ws"):
        return await call_next(request)
    
    response = await call_next(request)
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "whisper": ws_handler.whisper_service.health_check() if ws_handler else False,
            "deepseek": ws_handler.deepseek_service.health_check() if ws_handler else False
        }
    }

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = None):
    """
    WebSocket endpoint for real-time coaching
    
    Args:
        websocket: WebSocket connection
        client_id: Optional client identifier
    """
    if not client_id:
        client_id = str(uuid.uuid4())
    
    if ws_handler:
        await ws_handler.handle_connection(websocket, client_id)
    else:
        await websocket.close(code=1011, reason="Service not initialized")

# Knowledge Base endpoints
@app.get("/kb/search")
async def search_knowledge_base(query: str, max_results: int = 5):
    """Search knowledge base entries"""
    if not kb_service:
        return JSONResponse(
            status_code=503,
            content={"message": "Knowledge base not initialized"}
        )
    
    results = kb_service.search(query, max_results)
    return {
        "query": query,
        "results": [
            {
                "title": entry.title,
                "content": entry.content[:500],
                "category": entry.category,
                "tags": entry.tags
            }
            for entry in results
        ]
    }

@app.get("/kb/entries")
async def get_all_entries():
    """Get all knowledge base entries"""
    if not kb_service:
        return JSONResponse(
            status_code=503,
            content={"message": "Knowledge base not initialized"}
        )
    
    entries = kb_service.get_all_entries()
    return {
        "total": len(entries),
        "entries": [
            {
                "title": entry.title,
                "category": entry.category,
                "tags": entry.tags,
                "last_updated": entry.last_updated.isoformat()
            }
            for entry in entries
        ]
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

# Input sanitization helper
def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    import html
    return html.escape(text.strip())

# Run application
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.api.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level=config.LOG_LEVEL.lower()
    )
