# SentinAI 🤖

An autonomous AI agent project with a full-stack architecture, powered by LangChain, Google Gemini API, and Whisper AI.

## 🏛️ System Architecture

SentinAI implements a sophisticated pipeline for autonomous agent operations:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SentinAI Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   🎤 AUDIO   │───▶│  📝 TEXT     │───▶│  🧠 GEMINI   │───▶│ ⚡ ACTION │ │
│  │   (Whisper)  │    │  Processing  │    │    (LLM)     │    │  (Agent)  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └───────────┘ │
│         │                   │                   │                   │       │
│         ▼                   ▼                   ▼                   ▼       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        LangChain Orchestration                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pipeline Flow

| Stage | Component | Technology | Description |
|-------|-----------|------------|-------------|
| 1️⃣ **Audio Input** | `AudioProcessor` | Whisper AI | Transcribes voice commands to text with high accuracy |
| 2️⃣ **Text Processing** | `TextProcessor` | Python | Cleans, chunks, and extracts keywords from transcribed text |
| 3️⃣ **LLM Reasoning** | `GeminiAgent` | Google Gemini API | Processes context and generates intelligent responses |
| 4️⃣ **Action Execution** | `BaseAgent` | LangChain | Executes tasks based on LLM decisions and returns results |

### Data Flow Example

```
User speaks: "Schedule a meeting for tomorrow at 3pm"
    │
    ▼
[Whisper AI] ──▶ "Schedule a meeting for tomorrow at 3pm"
    │
    ▼
[Text Processor] ──▶ Extracts: {action: "schedule", time: "3pm", date: "tomorrow"}
    │
    ▼
[Gemini LLM] ──▶ Understands intent, plans action steps
    │
    ▼
[Agent] ──▶ Executes calendar API, confirms booking
    │
    ▼
Response: "Meeting scheduled for January 21, 2026 at 3:00 PM"
```

## 🏗️ Project Structure

```
SentinAI/
├── backend/                    # FastAPI Backend
│   ├── agents/                 # AI Agent logic
│   │   ├── base_agent.py       # Abstract base agent class
│   │   └── gemini_agent.py     # Google Gemini-powered agent
│   ├── processors/             # Data processing utilities
│   │   ├── audio_processor.py  # Whisper AI transcription
│   │   └── text_processor.py   # Text manipulation utilities
│   ├── api/                    # API layer
│   │   └── routes/             # API route handlers
│   │       ├── health.py       # Health check endpoints
│   │       └── agents.py       # Agent interaction endpoints
│   ├── data/                   # Temporary file storage (MLOps)
│   ├── models/                 # ML model weights storage (MLOps)
│   ├── main.py                 # FastAPI application entry point
│   └── requirements.txt        # Python dependencies
├── frontend/                   # Next.js Frontend
│   ├── app/                    # App Router pages
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page with chat interface
│   │   └── globals.css         # Global styles
│   ├── package.json            # Node.js dependencies
│   ├── tailwind.config.ts      # Tailwind CSS configuration
│   └── tsconfig.json           # TypeScript configuration
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Multi-container orchestration
└── README.md                   # This file
```

## 🚀 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML Tools**:
  - 🔗 LangChain - AI orchestration framework
  - 💎 Google Gemini API - Large language model
  - 🎤 Whisper AI - Speech-to-text transcription

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS

### DevOps
- **Containerization**: Docker & Docker Compose
- **MLOps**: Model versioning with `models/` directory

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn
- Docker (optional, for containerization)

## 🛠️ Installation

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
# Add GOOGLE_API_KEY=your_key_here
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## 🚀 Running the Application

### Option 1: Local Development

**Start Backend Server:**
```bash
cd backend
uvicorn main:app --reload
```

**Start Frontend Development Server:**
```bash
cd frontend
npm run dev
```

### Option 2: Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or for development mode
docker-compose --profile dev up
```

The application will be available at:
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/api/health` | Health check |
| GET | `/api/agents/status` | Agent status and capabilities |
| POST | `/api/agents/chat` | Send message to AI agent |

## 🔧 Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
DEBUG=True
LOG_LEVEL=INFO
```

## 📝 Development Notes

- CORS is configured to allow requests from `http://localhost:3000`
- The agents have placeholder implementations ready for Gemini API integration
- Whisper AI integration is scaffolded in `processors/audio_processor.py`
- MLOps directories (`data/`, `models/`) are tracked via `.gitkeep` files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this project for your own purposes.
