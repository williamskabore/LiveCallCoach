<p align="center">
  <img src="https://s13.gifyu.com/images/bdgbc.png" alt="Description of image" width="600"/>
</p>
# Real-Time Call Coach 🎯 by Williams KABORE

A production-ready agent assist dashboard that provides real-time transcription, AI-powered suggestions, and knowledge base integration for contact center agents.

## Features

- **Real-Time Transcription**: Browser microphone → Whisper API → Live transcript display
- **AI Coach**: DeepSeek V3 analyzes conversations and pushes contextual suggestions
- **Knowledge Base**: Hot-reloadable markdown files with search
- **Dashboard**: Clean React UI with live updates via WebSocket
- **Production Ready**: Docker, logging, rate limiting, error handling

## Prerequisites

- **Windows 10** with PowerShell 5.1+
- **Docker Desktop** for Windows (enable WSL2 backend)
- **Node.js** 18+ (for local frontend development only)
- **Git** (optional, for version control)

## Quick Start (Windows 10)

### 1. Install Dependencies

```powershell
# Install Docker Desktop
winget install Docker.DockerDesktop

# Install Node.js (if not present)
winget install OpenJS.NodeJS.LTS

# Verify installations
docker --version
node --version
npm --version

2. Clone & Configure
 
# Clone repository
git clone https://github.com/williamskabore/LiveCallCoach.git
cd LiveCallCoach

# Create environment file
copy .env.example .env

3. Edit .env file
 
WHISPER_API_KEY=sk-your-openai-key-here
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
REDIS_HOST=redis
REDIS_PORT=6379
LOG_LEVEL=INFO
MAX_RETRIES=3
RATE_LIMIT=10

4. Prepare Knowledge Base
Create markdown files in the kb/ directory:

# kb/greeting-scripts.md
## Standard Opening
"Thank you for calling [Company]. My name is [Name]. How can I assist you today?"

## Empathetic Opening
"I appreciate your patience. Let me help resolve this for you."

5. Build & Run
 
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
Usage Guide
Starting a Coaching Session
Click "Start Coaching" button
Grant microphone permission when prompted
Speak naturally - the system processes 5-second chunks
Watch the live transcript appear on the left
Receive AI suggestions on the right panel
Search knowledge base using the search bar
Understanding Coach Cards
Priority	Color	Action Needed
High	Red	Immediate attention
Medium	Yellow	Consider implementing
Low	Blue	Optional suggestion
Keyboard Shortcuts
Ctrl+Enter: Submit feedback for current suggestion
Esc: Dismiss all coach cards
Ctrl+F: Focus knowledge base search
Architecture
 

Browser Microphone → WebSocket → FastAPI Server
                                        ↓
                              ┌───────────────┐
                              │  Whisper API   │
                              │  (Transcription)│
                              └───────┬───────┘
                                      ↓
                              ┌───────────────┐
                              │  DeepSeek V3   │
                              │  (Analysis)    │
                              └───────┬───────┘
                                      ↓
                              ┌───────────────┐
                              │  Redis Cache   │
                              │  (State)       │
                              └───────┬───────┘
                                      ↓
                              WebSocket → React Dashboard
Production Considerations
Scaling
Horizontal scaling: Add more backend containers
Vertical scaling: Increase Redis memory (recommended 2GB)
Consider Azure/Google Cloud Speech-to-Text for enterprise
Monitoring
Logs: docker-compose logs - -f backend
Health check: curl http://localhost:8000/health
Metrics: /metrics endpoint (Prometheus format)
Security
All API keys stored in environment variables
WebSocket connections limited to allowed origins
Rate limiting: 10 API calls/minute/user
Input sanitization on all text fields

Troubleshooting:
Microphone not working
 
# Check browser permissions (Settings > Privacy > Microphone)
# Test with: https://mozilla.github.io/webrtc-landing/

Docker issues
 
# Restart Docker Desktop
# Reset to factory defaults if needed
# Check WSL2: wsl --list --verbose

API rate limits
 
# Check current usage in logs
docker-compose logs backend | findstr "rate_limit"
# Reduce rate in .env if needed
Development
Hot Reload
Backend: FastAPI auto-reload (set RELOAD=true in .env)
Frontend: Vite HMR enabled by default
Knowledge base: Watches kb/ directory every 5 seconds
Adding New Features
Create feature branch: git checkout -b feature/your-feature
Update backend services in backend/services/
Add frontend components in frontend/src/components/
Write tests in respective tests/ directories
Submit PR with description and test results

License
MIT - See LICENSE file for details

Support
Author: Williams R.D. KABORE
Documentation: /docs directory

Enterprise Support & Setup Assistance:
williams.kabore@welcdn.com

