<p align="center">
  <img src="https://s13.gifyu.com/images/bdgbc.png" alt="Real-Time Call Coach Dashboard" width="600"/>
</p>

<h1 align="center">Real-Time Call Coach 🎯 by Williams KABORE</h1>

<p align="center">
  <em>A production-ready agent assist dashboard providing real-time transcription, AI-powered suggestions, and knowledge base integration for contact center agents.</em>
</p>

---

## ✨ Features

- **Real-Time Transcription** - Browser microphone → Whisper API → Live transcript display
- **AI Coach** - DeepSeek V3 analyzes conversations and pushes contextual suggestions
- **Knowledge Base** - Hot-reloadable markdown files with search
- **Dashboard** - Clean React UI with live updates via WebSocket
- **Production Ready** - Docker, logging, rate limiting, error handling

## 📋 Prerequisites

| Requirement | Version/Details |
|-------------|-----------------|
| **Windows 10** | PowerShell 5.1+ |
| **Docker Desktop** | Enable WSL2 backend |
| **Node.js** | 18+ (local frontend development only) |
| **Git** | Optional, for version control |

## 🚀 Quick Start (Windows 10)

### 1. Install Dependencies

```powershell
# Install Docker Desktop
winget install Docker.DockerDesktop
```
# Install Node.js (if not present)
```
winget install OpenJS.NodeJS.LTS
 ```
# Verify installations
```
docker --version
node --version
npm --version
```
2. Clone & Configure
 

# Clone repository
git clone https://github.com/williamskabore/LiveCallCoach.git
cd LiveCallCoach

# Create environment file
```
copy .env.example .env
```
# 3. Edit .env file
```
WHISPER_API_KEY=sk-your-openai-key-here
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
REDIS_HOST=redis
REDIS_PORT=6379
LOG_LEVEL=INFO
MAX_RETRIES=3
RATE_LIMIT=10
```
# 4. Prepare Knowledge Base
Create markdown files in the kb/ directory:
```
# kb/greeting-scripts.md
## Standard Opening
"Thank you for calling [Company]. My name is [Name]. How can I assist you today?"

## Empathetic Opening
"I appreciate your patience. Let me help resolve this for you."
```
# 5. Build & Run
 
# Build Docker images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Access dashboard
# Open browser to http://localhost:5173
6. Run Tests
 
# Backend tests
docker-compose exec backend pytest tests/

# Frontend tests
docker-compose exec frontend npm test
📖 Usage Guide
Starting a Coaching Session
Click "Start Coaching" button
Grant microphone permission when prompted
Speak naturally - the system processes 5-second chunks
Watch the live transcript appear on the left
Receive AI suggestions on the right panel
Search knowledge base using the search bar
Understanding Coach Cards
Priority	Color	Action Needed
High	🔴 Red	Immediate attention
Medium	🟡 Yellow	Consider implementing
Low	🔵 Blue	Optional suggestion
Keyboard Shortcuts
Shortcut	Action
Ctrl+Enter	Submit feedback for current suggestion
Esc	Dismiss all coach cards
Ctrl+F	Focus knowledge base search

# 🏗 Architecture
 
graph TD
    A[Browser Microphone] -->|WebSocket| B[FastAPI Server]
    B --> C[Whisper API - Transcription]
    C --> D[DeepSeek V3 - Analysis]
    D --> E[Redis Cache - State]
    E -->|WebSocket| F[React Dashboard]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width::2px
    style E fill:#bff,stroke:#333,stroke-width:2px
    style F fill:#ffb,stroke:#333,stroke-width:2px
# 🛠 Production Considerations
# Scaling
Horizontal scaling: Add more backend containers
Vertical scaling: Increase Redis memory (recommended 2GB)
Enterprise: Consider Azure/Google Cloud Speech-to-Text
Monitoring
 
# Logs
```
docker-compose logs -f backend
```
# Health check
```
curl http://localhost:8000/health
```
# Metrics
# /metrics endpoint (Prometheus format)
# Security
✅ All API keys stored in environment variables
✅ WebSocket connections limited to allowed origins
✅ Rate limiting: 10 API calls/minute/user
✅ Input sanitization on all text fields

# 🔧 Troubleshooting
# Microphone not working
 
# Check browser permissions (Settings > Privacy > Microphone)
# Test with: https://mozilla.github.io/webrtc-landing/

# Docker issues
 
# Restart Docker Desktop
# Reset to factory defaults if needed
# Check WSL2: wsl --list --verbose

# API rate limits
 
# Check current usage in logs
docker-compose logs backend | findstr "rate_limit"

# Reduce rate in .env if needed
# 💻 Development
Hot Reload
Backend: FastAPI auto auto-reload (set RELOAD=true in .env)
Frontend: Vite HMR enabled by default
Knowledge base: Watches kb/ directory every 5 seconds

# Adding New Features
Create feature branch: git checkout -b feature/your-feature
Update backend services in backend/services/
Add frontend components in frontend/src/components/
Write tests in respective tests/ directories
Submit PR with description and test results
# 📄 License
MIT - See LICENSE file for details

👨‍💻 Support
Author: Williams R.D. KABORE
Documentation: /docs directory

# Enterprise Support & Setup Assistance:
📧
williams.kabore@welcdn.com

<p align="center"> <sub>Built with ❤️ for contact center agents worldwide</sub> </p>
