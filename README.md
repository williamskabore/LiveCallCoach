<center><p align="center">
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
# 2. Clone & Configure
 

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

# kb/greeting-scripts.md
## Standard Opening
"Thank you for calling [Company]. My name is [Name]. How can I assist you today?"

## Empathetic Opening
"I appreciate your patience. Let me help resolve this for you."

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
docker-compose exec frontend npm test<br>
📖 Usage Guide<br>
Starting a Coaching Session<br>
Click "Start Coaching" button<br>
Grant microphone permission when prompted<br>
Speak naturally - the system processes 5-second chunks<br>
Watch the live transcript appear on the left<br>
Receive AI suggestions on the right panel<br>
Search knowledge base using the search bar<br>
Understanding Coach Cards<br>
Priority	Color	Action Needed<br>
High	🔴 Red	Immediate attention<br>
Medium	🟡 Yellow	Consider implementing<br>
Low	🔵 Blue	Optional suggestion<br>
Keyboard Shortcuts<br>
Shortcut	Action<br>
Ctrl+Enter	Submit feedback for current suggestion<br>
Esc	Dismiss all coach cards<br>
Ctrl+F	Focus knowledge base search<br>

# 🏗 Architecture
 
graph TD
    A[Browser Microphone] -->|WebSocket| B[FastAPI Server]<br>
    B --> C[Whisper API - Transcription]<br>
    C --> D[DeepSeek V3 - Analysis]<br>
    D --> E[Redis Cache - State]<br>
    E -->|WebSocket| F[React Dashboard]<br>


# 🛠 Production Considerations
# Scaling
Horizontal scaling: Add more backend containers<br>
Vertical scaling: Increase Redis memory (recommended 2GB)<br>
Enterprise: Consider Azure/Google Cloud Speech-to-Text<br>
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
  /metrics endpoint (Prometheus format)
# Security
✅ All API keys stored in environment variables<br>
✅ WebSocket connections limited to allowed origins<br>
✅ Rate limiting: 10 API calls/minute/user<br>
✅ Input sanitization on all text fields<br>

# 🔧 Troubleshooting
# Microphone not working
 
 Check browser permissions (Settings > Privacy > Microphone)
 Test with: https://mozilla.github.io/webrtc-landing/

# Docker issues
  Restart Docker Desktop
  Reset to factory defaults if needed
  Check WSL2: wsl --list --verbose

# API rate limits
  Check current usage in logs
  docker-compose logs backend | findstr "rate_limit"

# Reduce rate in .env if needed
# 💻 Development
  Hot Reload
  Backend: FastAPI auto auto-reload (set RELOAD=true in .env)
  Frontend: Vite HMR enabled by default
  Knowledge base: Watches kb/ directory every 5 seconds

# Adding New Features
  Create feature branch: git checkout -b feature/your-feature<br>
  Update backend services in backend/services/<br>
  Add frontend components in frontend/src/components/<br>
  Write tests in respective tests/ directories<br>
  Submit PR with description and test results<br>

# 📄 License
  MIT - See LICENSE file for details

👨‍💻 Support
  Author: Williams R.D. KABORE
  Documentation: /docs directory

# Enterprise Support & Setup Assistance:
  📧
  williams.kabore@welcdn.com

<p align="center"> <sub>Built with ❤️ for contact center agents worldwide</sub> </p>
</center>
