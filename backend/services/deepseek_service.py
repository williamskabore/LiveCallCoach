import logging
import json
from typing import Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.config import config
from backend.api.models import DeepSeekResponse, Suggestion, SuggestionPriority

logger = logging.getLogger(__name__)

class DeepSeekService:
    def __init__(self):
        self.api_key = config.DEEPSEEK_API_KEY
        self.api_url = config.DEEPSEEK_API_URL
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def analyze_transcription(self, text: str, context: Optional Optional[dict] = None) -> DeepSeekResponse:
        """
        Analyze transcription text using DeepSeek V3
        """
        try:
            prompt = self._build_analysis_prompt(text, context)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an expert call center coach AI. Analyze the conversation and provide:
                        1. Next-best-action suggestions with priority levels
                        2. Customer sentiment score (-1 to 1)
                        3. Call intent detection
                        
                        Respond in JSON format only."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 500,
                "response_format": {"type": "json_object"}
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = json.loads(result["choices"][0]["message"]["content"])
                    return self._parse_response(content)
                else:
                    logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                    raise Exception(f"DeepSeek API returned {response.status_code}")
                    
        except Exception as e:
            logger.error(f"DeepSeek analysis error: {str(e)}")
            # Return fallback response
            return self._get_fallback_response()
    
    def _build_analysis_prompt(self, text: str, context: Optional[dict]) -> str:
               """Build analysis prompt with context"""
        prompt = f"Analyze this call center conversation:\n
{text}\n
"
        
        if context:
            prompt += f"Context:\n- Call duration: {context.get('duration', 'N/A')}\n"
            prompt += f"- Previous suggestions: {context.get('previous_suggestions', 'None')}\n"
            
        return prompt
    
    def _parse_response(self, content: dict) -> DeepSeekResponse:
        """Parse and validate DeepSeek response"""
        suggestions = []
        for sugg in content.get("suggestions", []):
            suggestions.append(Suggestion(
                text=sugg.get("text", ""),
                priority=SuggestionPriority(sugg.get("priority", "low")),
                category=sugg.get("category", "general"),
                timestamp=sugg.get("timestamp", 0)
            ))
        
        return DeepSeekResponse(
            suggestions=suggestions,
            sentiment=float(content.get("sentiment", 0)),
            intent=content.get("intent", "")
        )
    
    def _get_fallback_response(self) -> DeepSeekResponse:
        """Return fallback response when API fails"""
        return DeepSeekResponse(
            suggestions=[
                Suggestion(
                    text="Unable to analyze, using cached rules",
                    priority=SuggestionPriority.LOW,
                    category="system",
                    timestamp=0
                )
            ],
            sentiment=0.0,
            intent="unknown"
        )
    
    async def health_check(self) -> bool:
        """Check if DeepSeek API is accessible"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.deepseek.com/v1/models",
                    headers=headers,
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"DeepSeek health check failed: {str(e)}")
            return False
