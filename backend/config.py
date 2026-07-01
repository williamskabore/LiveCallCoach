import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"
    
    # Server Config
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8000))
    
    # WebSocket
    WS_MAX_CONNECTIONS = 100
    WS_RECONNECT_DELAY = 3  # seconds
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = 10
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # Audio Config
    AUDIO_CHUNK_DURATION = 5  # seconds
    AUDIO_SAMPLE_RATE = 16000
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # Knowledge Base
    KB_DIRECTORY = "/app/kb"
    KB_WATCH_ENABLED = True
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "/app/logs/call_coach.log"
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

config = Config()
```

**backend/requirements.txt**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
redis==5.0.1
python-multipart==0.0.6
python-dotenv==1.0.0
httpx==0.25.2
pydantic==2.5.2
pydantic-settings==2.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
watchfiles==0.21.0
tenacity==8.2.3
