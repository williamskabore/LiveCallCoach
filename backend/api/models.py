from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AudioChunk(BaseModel):
    data: str  # Base64 encoded audio
    timestamp: float
    sequence: int

class TranscriptionResult(BaseModel):
    text: str
    confidence: float
    timestamp: float
    speaker: Optional[str] = None

class SuggestionPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Suggestion(BaseModel):
    text: str
    priority: SuggestionPriority
    category: str
    timestamp: float

class DeepSeekResponse(BaseModel):
    suggestions: List[Suggestion] = Field(default_factory=list)
    sentiment: float = Field(ge=-1.0, le=1.0)
    intent: str = ""
    
class CoachMessage(BaseModel):
    type: str  # "transcription", "suggestion", "metrics", "error"
    data: Dict[str, Any]
    timestamp: float = Field(default_factory=datetime.now().timestamp)

class CallMetrics(BaseModel):
    aht: float = 0.0  # Average Handling Time
    sentiment_score: float = 0.0
    compliance_flag: bool = False
    call_duration: float = 0.0
    active_suggestions: int = 0

class KnowledgeBaseEntry(BaseModel):
    title: str
    content: str
    category: str
    tags: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
