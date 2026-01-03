from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class Agent1Request(BaseModel):
    user_id: str
    question_id: str
    student_answer: str
    topic: str
    difficulty: str


class Agent1Response(BaseModel):
    solution: str
    explanation: str
    confidence: float


class Agent2Request(BaseModel):
    user_id: str
    question_id: str
    current_hint_level: int
    student_answer: str
    topic: str
    difficulty: str


class Agent2Response(BaseModel):
    hint: str
    hint_level: int
    max_hints: int
    next_available: bool


class Agent3Request(BaseModel):
    user_id: str
    question_id: str
    step_number: int
    student_answer: str
    time_taken: Optional[int] = None


class Agent3Response(BaseModel):
    hesitation_detected: bool
    hesitation_score: float
    prolonged_hesitation: bool


class Agent4Request(BaseModel):
    user_id: str
    question_id: str
    step_number: int
    student_answer: str
    hint_level: int
    hesitation_score: Optional[float] = None


class Agent4Response(BaseModel):
    stuck_score: int
    stuck_level: str
    needs_intervention: bool


class Agent5Request(BaseModel):
    user_id: str
    question_id: str
    student_answer: str
    correct_answer: str
    topic: str
    mistake_history: Optional[List[Dict[str, Any]]] = None


class Agent5Response(BaseModel):
    mistake_pattern: str
    pattern_strength: float
    repeated_mistake: bool
    learning_gap: str


class Agent6Request(BaseModel):
    user_id: str
    topic: Optional[str] = None
    time_range: Optional[int] = None


class Agent6Response(BaseModel):
    progress_data: Dict[str, Any]
    mastery_levels: Dict[str, float]
    learning_velocity: float
    time_spent: int


class Agent7Request(BaseModel):
    user_id: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    mistake_patterns: Optional[List[str]] = None


class Agent7Response(BaseModel):
    flashcards: List[Dict[str, Any]]
    priority_topics: List[str]
    review_count: int
    next_review: str


class Agent8Request(BaseModel):
    user_id: str
    question_id: str
    topic: str
    trigger_reason: str
    context: Dict[str, Any]


class Agent8Response(BaseModel):
    action: str
    video_ref: Optional[str] = None
    youtube_metadata: Optional[Dict[str, Any]] = None
    explanation: str
