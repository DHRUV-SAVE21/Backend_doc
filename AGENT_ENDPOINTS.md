# 🤖 AI Agent Endpoints Reference

## Complete List of All 8 n8n Agent Webhooks

### 🔗 Production Webhook URLs

| Agent | Purpose | Webhook URL | Method |
|-------|---------|-------------|--------|
| **Agent 1** | Direct Doubt Resolver | `http://localhost:5678/webhook/agent1/submit-doubt` | POST |
| **Agent 2** | Hint Strategy Agent | `http://localhost:5678/webhook/agent2/get-hint` | POST |
| **Agent 3** | Hesitation Detector | `http://localhost:5678/webhook/agent3/hesitation` | POST |
| **Agent 4** | Stuck Score Calculator | `http://localhost:5678/webhook/agent4/stuck-score` | POST |
| **Agent 5** | Mistake Pattern Learner | `http://localhost:5678/webhook/agent5/mistake-pattern` | POST |
| **Agent 6** | Progress Tracker | `http://localhost:5678/webhook/agent6/progress` | POST |
| **Agent 7** | Flashcard Recommender | `http://localhost:5678/webhook/agent7/flashcards` | POST |
| **Agent 8** | Video Intelligence Agent | `http://localhost:5678/webhook/agent8/video-intelligence` | POST |

---

## 📋 Agent Details & Request/Response Schemas

### 🧠 Agent 1 – Direct Doubt Resolver
**Webhook**: `POST http://localhost:5678/webhook/agent1/submit-doubt`

**Request Schema**:
```json
{
    "user_id": "string",
    "question_id": "string", 
    "student_answer": "string",
    "topic": "string",
    "difficulty": "string"
}
```

**Response Schema**:
```json
{
    "solution": "string",
    "explanation": "string", 
    "confidence": "float (0.0-1.0)"
}
```

---

### 💡 Agent 2 – Hint Strategy Agent  
**Webhook**: `POST http://localhost:5678/webhook/agent2/get-hint`

**Request Schema**:
```json
{
    "user_id": "string",
    "question_id": "string",
    "current_hint_level": "integer",
    "student_answer": "string", 
    "topic": "string",
    "difficulty": "string"
}
```

**Response Schema**:
```json
{
    "hint": "string",
    "hint_level": "integer",
    "max_hints": "integer",
    "next_available": "boolean"
}
```

---

### ⏱️ Agent 3 – Hesitation Detector
**Webhook**: `POST http://localhost:5678/webhook/agent3/hesitation`

**Request Schema**:
```json
{
    "user_id": "string",
    "question_id": "string",
    "step_number": "integer",
    "student_answer": "string",
    "time_taken": "integer (optional)"
}
```

**Response Schema**:
```json
{
    "hesitation_detected": "boolean",
    "hesitation_score": "float",
    "prolonged_hesitation": "boolean"
}
```

---

### 📊 Agent 4 – Stuck Score Calculator
**Webhook**: `POST http://localhost:5678/webhook/agent4/stuck-score`

**Request Schema**:
```json
{
    "user_id": "string",
    "question_id": "string", 
    "step_number": "integer",
    "student_answer": "string",
    "hint_level": "integer",
    "hesitation_score": "float (optional)"
}
```

**Response Schema**:
```json
{
    "stuck_score": "integer (0-100)",
    "stuck_level": "string",
    "needs_intervention": "boolean"
}
```

---

### 🧩 Agent 5 – Mistake Pattern Learner
**Webhook**: `POST http://localhost:5678/webhook/agent5/mistake-pattern`

**Request Schema**:
```json
{
    "user_id": "string",
    "question_id": "string",
    "student_answer": "string", 
    "correct_answer": "string",
    "topic": "string",
    "mistake_history": "array (optional)"
}
```

**Response Schema**:
```json
{
    "mistake_pattern": "string",
    "pattern_strength": "float",
    "repeated_mistake": "boolean", 
    "learning_gap": "string"
}
```

---

### 📈 Agent 6 – Progress Tracker
**Webhook**: `POST http://localhost:5678/webhook/agent6/progress`

**Request Schema**:
```json
{
    "user_id": "string",
    "topic": "string (optional)",
    "time_range": "integer (optional)"
}
```

**Response Schema**:
```json
{
    "progress_data": "object",
    "mastery_levels": "object",
    "learning_velocity": "float",
    "time_spent": "integer"
}
```

---

### 🎴 Agent 7 – Flashcard Recommender
**Webhook**: `POST http://localhost:5678/webhook/agent7/flashcards`

**Request Schema**:
```json
{
    "user_id": "string",
    "topic": "string (optional)",
    "difficulty": "string (optional)",
    "mistake_patterns": "array (optional)"
}
```

**Response Schema**:
```json
{
    "flashcards": "array",
    "priority_topics": "array",
    "review_count": "integer",
    "next_review": "string"
}
```

---

### 🎥 Agent 8 – Video Intelligence Agent
**Webhook**: `POST http://localhost:5678/webhook/agent8/video-intelligence`

**Request Schema**:
```json
{
    "user_id": "string",
    "question_id": "string",
    "topic": "string", 
    "trigger_reason": "string",
    "context": "object"
}
```

**Response Schema**:
```json
{
    "action": "string (SHOW_YOUTUBE | GENERATE_VIDEO)",
    "video_ref": "string (optional)",
    "youtube_metadata": "object (optional)",
    "explanation": "string"
}
```

---

## 🚨 Important Notes

### ✅ Production Webhooks Only
- All endpoints use `/webhook/` prefix (NOT `/webhook-test/`)
- No "Listen for test event" required
- All workflows should be ACTIVATED in n8n

### 🔄 Agent 8 Special Logic
Agent 8 is NEVER called directly by frontend. Backend triggers Agent 8 when:
- `hint_level` exhausted (≥4)
- `prolonged_hesitation` from Agent 3
- `high_stuck_score` (>70) from Agent 4  
- `repeated_mistake_pattern` from Agent 5
- `user_intent == "video"`

### 📡 Testing Webhooks
You can test individual webhooks with curl:
```bash
# Test Agent 1
curl -X POST http://localhost:5678/webhook/agent1/submit-doubt \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question_id":"q1","student_answer":"help","topic":"test","difficulty":"easy"}'
```

### 🔧 Backend Integration
- Backend calls these webhooks via `app/services/n8n_client.py`
- All calls are async with retry logic
- Responses are logged to MongoDB for analytics
- Error handling with exponential backoff

---

## 🎯 Quick Verification Checklist

- [ ] n8n running on `localhost:5678`
- [ ] All 8 workflows activated
- [ ] Production webhooks accessible (no `/test` suffix)
- [ ] Backend can reach all endpoints
- [ ] MongoDB running on `localhost:27017`
- [ ] Backend logs show successful agent calls

**🚀 All 8 agents ready for orchestration!**
