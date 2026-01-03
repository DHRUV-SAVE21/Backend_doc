# AI Education Platform Backend

A production-ready FastAPI backend that orchestrates 8 AI agents (hosted in n8n) into 5 user-facing features for an AI-powered education platform.

## 🚀 Features

### 5 User-Facing Features
1. **Live Doubt Resolution** - Direct solution for student doubts
2. **Guided Problem Solving** - 4-level progressive hint system
3. **Adaptive Video Assistance** - Context-aware video recommendations
4. **Self-Improving System** - Progress tracking and analytics
5. **Progress & Revision** - Dashboard with flashcard recommendations

### 8 AI Agents (n8n Workflows)
- **Agent 1** – Direct Doubt Resolver: `/webhook/agent1/submit-doubt`
- **Agent 2** – Hint Strategy Agent: `/webhook/agent2/get-hint`
- **Agent 3** – Hesitation Detector: `/webhook/agent3/hesitation`
- **Agent 4** – Stuck Score Calculator: `/webhook/agent4/stuck-score`
- **Agent 5** – Mistake Pattern Learner: `/webhook/agent5/mistake-pattern`
- **Agent 6** – Progress Tracker: `/webhook/agent6/progress`
- **Agent 7** – Flashcard Recommender: `/webhook/agent7/flashcards`
- **Agent 8** – Video Intelligence Agent: `/webhook/agent8/video-intelligence`

## 📋 Prerequisites

- Python 3.8+
- MongoDB (running on localhost:27017)
- n8n (running on localhost:5678 with all 8 agent workflows activated)
- Git

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd backend_shetty
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env` file and update as needed:
```bash
# The .env file is already configured for local development
# Update these values for your production environment
```

### 5. Start MongoDB
```bash
# Make sure MongoDB is running on localhost:27017
mongod
```

### 6. Verify n8n Workflows
Ensure all 8 n8n workflows are activated and accessible at:
- `http://localhost:5678/webhook/agent1/submit-doubt`
- `http://localhost:5678/webhook/agent2/get-hint`
- `http://localhost:5678/webhook/agent3/hesitation`
- `http://localhost:5678/webhook/agent4/stuck-score`
- `http://localhost:5678/webhook/agent5/mistake-pattern`
- `http://localhost:5678/webhook/agent6/progress`
- `http://localhost:5678/webhook/agent7/flashcards`
- `http://localhost:5678/webhook/agent8/video-intelligence`

## 🚀 Running the Application

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The application will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Feature | Description |
|--------|----------|---------|-------------|
| POST | `/api/doubt` | Live Doubt Resolution | Direct doubt solving |
| POST | `/api/problem/solve` | Guided Problem Solving | Step-by-step guidance |
| POST | `/api/problem/hint` | Progressive Hints | Level-based hints |
| POST | `/api/problem/progress` | Progress Updates | Track solving progress |
| POST | `/api/video/assist` | Video Assistance | Context-aware videos |
| POST | `/api/progress` | Progress Tracking | Learning analytics |
| GET | `/api/dashboard` | Dashboard | Overview & flashcards |
| POST | `/api/dashboard` | Dashboard (POST) | Alternative dashboard endpoint |

## 🧪 Postman Testing

### Setup
1. Import the provided Postman collection or create requests manually
2. Set base URL: `http://localhost:8000`
3. Use the request examples below

### Test Examples

#### 1. Live Doubt Resolution
```http
POST http://localhost:8000/api/doubt
Content-Type: application/json

{
    "user_id": "u123",
    "question_id": "q101",
    "step_number": 1,
    "student_answer": "I don't understand binary search",
    "intent": "direct_solution",
    "topic": "Binary Search",
    "difficulty": "medium"
}
```

#### 2. Guided Problem Solving
```http
POST http://localhost:8000/api/problem/solve
Content-Type: application/json

{
    "user_id": "u123",
    "question_id": "q101",
    "step_number": 2,
    "student_answer": "I'm stuck at the recursion step",
    "intent": "guided",
    "topic": "Binary Search",
    "difficulty": "medium"
}
```

#### 3. Progressive Hints
```http
POST http://localhost:8000/api/problem/hint
Content-Type: application/json

{
    "user_id": "u123",
    "question_id": "q101",
    "step_number": 2,
    "student_answer": "I'm confused about the base case",
    "intent": "guided",
    "topic": "Binary Search",
    "difficulty": "medium",
    "current_hint_level": 1
}
```

#### 4. Video Assistance
```http
POST http://localhost:8000/api/video/assist
Content-Type: application/json

{
    "user_id": "u123",
    "question_id": "q101",
    "step_number": 2,
    "student_answer": "I need to see this explained visually",
    "intent": "video",
    "topic": "Binary Search",
    "difficulty": "medium",
    "video_context": "recursive implementation",
    "timestamp": 120
}
```

#### 5. Progress Tracking
```http
POST http://localhost:8000/api/progress
Content-Type: application/json

{
    "user_id": "u123",
    "topic": "Binary Search",
    "time_range": 7
}
```

#### 6. Dashboard
```http
GET http://localhost:8000/api/dashboard?user_id=u123&topic=Binary%20Search
```

### Expected Response Format
```json
{
    "mode": "HINT | SOLUTION | VIDEO | FLASHCARD",
    "content": "Response content...",
    "hint_level": 2,
    "stuck_score": 65,
    "video_ref": "ai_video_12345",
    "analytics": {
        "agent": "agent2",
        "response_time": 1.2
    },
    "timestamp": "2024-01-04T03:49:00.000Z"
}
```

## 🔧 Architecture

### Backend as Single Orchestrator
- **Frontend/Postman** → **FastAPI Backend** → **n8n Agents** → **FastAPI Backend** → **Frontend/Postman**
- Agents never call each other directly
- Frontend never calls agents directly
- All intelligence is orchestrated through the backend

### Agent 8 Special Logic
Agent 8 (Video Intelligence) is triggered automatically when:
- Hint level is exhausted (4/4)
- Prolonged hesitation detected
- High stuck score (>70)
- Repeated mistake patterns
- User explicitly requests video

### Data Flow
1. Request received at FastAPI endpoint
2. Agent Router decides which agent(s) to call
3. n8n Client makes HTTP calls to production webhooks
4. Responses are merged and processed
5. MongoDB logs all interactions for analytics
6. Clean JSON response returned

## 🗂️ Project Structure

```
backend_shetty/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # Application settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── mongodb.py             # MongoDB service
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── doubt.py               # Doubt resolution endpoints
│   │   ├── problem.py             # Problem solving endpoints
│   │   ├── video.py               # Video assistance endpoints
│   │   ├── progress.py            # Progress tracking endpoints
│   │   └── dashboard.py           # Dashboard endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── requests.py            # Request models
│   │   ├── responses.py           # Response models
│   │   └── agent_schemas.py       # Agent-specific models
│   └── services/
│       ├── __init__.py
│       ├── n8n_client.py          # HTTP client for n8n
│       └── agent_router.py         # Central decision engine
├── main.py                         # FastAPI application
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
└── README.md                      # This file
```

## 🐛 Common Issues & Fixes

### 1. MongoDB Connection Error
**Error**: `ServerSelectionTimeoutError`
**Fix**: Ensure MongoDB is running on localhost:27017
```bash
# Start MongoDB
mongod
```

### 2. n8n Connection Timeout
**Error**: `Timeout calling agent`
**Fix**: 
- Verify n8n is running on localhost:5678
- Check that all 8 workflows are activated
- Ensure webhook URLs are correct (no `/test` suffix)

### 3. Agent Response Errors
**Error**: `HTTP 404 from n8n`
**Fix**: 
- Verify webhook paths match exactly
- Check n8n workflow activation status
- Ensure production webhooks (not test webhooks)

### 4. Import Errors
**Error**: `ModuleNotFoundError`
**Fix**: 
- Install all dependencies: `pip install -r requirements.txt`
- Activate virtual environment
- Check Python path

### 5. Port Already in Use
**Error**: `Address already in use`
**Fix**: 
- Kill process on port 8000: `netstat -ano | findstr :8000`
- Use different port: `uvicorn main:app --port 8001`

## 📊 Monitoring & Logging

### Application Logs
- Logs are written to console by default
- Configure log level in `.env`: `LOG_LEVEL=INFO`
- All agent calls are logged with response times

### MongoDB Analytics
- All user interactions are stored
- Agent performance metrics tracked
- Progress analytics available via dashboard

### Health Monitoring
- Health check endpoint: `GET /health`
- Returns application status and version
- Monitors MongoDB connectivity

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
```bash
N8N_BASE_URL=https://your-n8n-instance.com
MONGODB_URL=mongodb://your-mongodb-cluster
DEBUG=false
SECRET_KEY=your-production-secret-key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the Common Issues section above
2. Review the API documentation at `/docs`
3. Check n8n workflow status
4. Verify MongoDB connectivity

---

**🎯 Ready for Hackathon!**

This backend is fully functional and ready for integration with your frontend. All 8 n8n agents are orchestrated into 5 clean features, with comprehensive logging and analytics built-in.
