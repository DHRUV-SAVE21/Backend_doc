from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class UserIntent(str, Enum):
    GUIDED = "guided"
    DIRECT_SOLUTION = "direct_solution"
    VIDEO = "video"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class BaseRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    question_id: str = Field(..., description="Question identifier")
    step_number: int = Field(default=1, description="Current step in problem solving")
    student_answer: str = Field(..., description="Student's current answer or input")
    intent: UserIntent = Field(..., description="User's learning intent")
    topic: str = Field(..., description="Topic being studied")
    difficulty: Difficulty = Field(..., description="Difficulty level")


class DoubtRequest(BaseRequest):
    pass


class ProblemSolveRequest(BaseRequest):
    pass


class HintRequest(BaseRequest):
    current_hint_level: Optional[int] = Field(default=0, description="Current hint level reached")


class ProgressRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    topic: Optional[str] = Field(None, description="Filter by topic")
    time_range: Optional[int] = Field(default=7, description="Days of progress to fetch")


class VideoAssistRequest(BaseRequest):
    video_context: Optional[str] = Field(None, description="Additional video context")
    timestamp: Optional[int] = Field(None, description="Video timestamp in seconds")


class DashboardRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
