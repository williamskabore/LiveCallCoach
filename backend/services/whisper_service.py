import logging
import base64
import io
import wave
from typing import Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.config import config

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        self.api_url = config.WHISPER_API_URL
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def transcribe_audio(self, audio_base64: str) -> dict:
        """
        Transcribe audio chunk using OpenAI Whisper API
        """
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            
            # Prepare audio file for API
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"
            
            # Create multipart form data
            files = {
                "file": ("audio.wav", audio_bytes, "audio/wav"),
                "model": (None, "whisper-1"),
                "response_format": (None, "verbose_json"),
                "language": (None, "en"),
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "text": result.get("text", ""),
                        "confidence": self._calculate_confidence(result),
                        "segments": result.get("segments", [])
                    }
                else:
                    logger.error(f"Whisper API error: {response.status_code} - {response.text}")
                    raise Exception(f"Whisper API returned {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise
    
    def _calculate_confidence(self, result: dict) -> float:
        """
        Calculate overall confidence from segments
        """
        segments = result.get("segments", [])
        if not segments:
            return 0.0
        
        confidences = [seg.get("confidence", 0) for seg in segments]
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    async def health_check(self) -> bool:
        """
        Check if Whisper API is accessible
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers=headers,
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Whisper health check failed: {str(e)}")
            return False
