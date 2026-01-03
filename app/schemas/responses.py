from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AgentResponse(BaseModel):
    success: bool = Field(..., description="Whether the agent call was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Agent response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    agent_name: str = Field(..., description="Name of the agent that responded")


class BaseResponse(BaseModel):
    mode: str = Field(..., description="Response mode: HINT, SOLUTION, VIDEO, FLASHCARD")
    content: str = Field(..., description="Main response content")
    analytics: Dict[str, Any] = Field(default_factory=dict, description="Analytics data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class DoubtResponse(BaseResponse):
    mode: str = Field(default="SOLUTION", description="Response mode for doubt resolution")
    confidence_score: Optional[float] = Field(None, description="Confidence in the solution")


class HintResponse(BaseResponse):
    mode: str = Field(default="HINT", description="Response mode for hints")
    hint_level: int = Field(..., description="Current hint level (1-4)")
    next_hint_available: bool = Field(..., description="Whether more hints are available")
    stuck_score: Optional[int] = Field(None, description="Student's stuck score")


class ProblemSolveResponse(BaseResponse):
    mode: str = Field(default="SOLUTION", description="Response mode for problem solving")
    steps: List[str] = Field(default_factory=list, description="Step-by-step solution")
    hint_level: Optional[int] = Field(None, description="Hint level that led to solution")
    stuck_score: Optional[int] = Field(None, description="Final stuck score")


class VideoAssistResponse(BaseResponse):
    mode: str = Field(default="VIDEO", description="Response mode for video assistance")
    video_ref: Optional[str] = Field(None, description="Internal video reference")
    youtube_metadata: Optional[Dict[str, Any]] = Field(None, description="YouTube video metadata")
    action: str = Field(..., description="Action: SHOW_YOUTUBE or GENERATE_VIDEO")


class ProgressResponse(BaseModel):
    user_id: str = Field(..., description="User identifier")
    progress_data: Dict[str, Any] = Field(..., description="Progress analytics")
    strengths: List[str] = Field(default_factory=list, description="User's strong topics")
    weaknesses: List[str] = Field(default_factory=list, description="Topics needing improvement")
    recommendations: List[str] = Field(default_factory=list, description="Learning recommendations")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class DashboardResponse(BaseModel):
    user_id: str = Field(..., description="User identifier")
    overview: Dict[str, Any] = Field(..., description="Dashboard overview")
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Recent learning activity")
    progress_summary: Dict[str, Any] = Field(..., description="Progress summary")
    flashcard_recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Flashcard recommendations")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
