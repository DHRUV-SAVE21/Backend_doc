from fastapi import APIRouter, HTTPException
from app.services.agent_router import agent_router
from app.schemas.requests import VideoAssistRequest
from app.schemas.responses import VideoAssistResponse, ErrorResponse
from app.models.mongodb import mongodb_service
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video", tags=["video"])


@router.post("/assist", response_model=VideoAssistResponse)
async def video_assistance(request: VideoAssistRequest):
    """
    FEATURE 3: Adaptive Video Assistance
    
    Provides video assistance using Agent 8 (Video Intelligence).
    Triggered by user request or system-detected learning difficulties.
    
    Example Postman Request:
    POST http://localhost:8000/api/video/assist
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
    """
    start_time = time.time()
    
    try:
        # Log incoming request
        await mongodb_service.log_user_activity(
            user_id=request.user_id,
            activity_data={
                "activity_type": "video_assistance",
                "question_id": request.question_id,
                "topic": request.topic,
                "difficulty": request.difficulty.value,
                "video_context": request.video_context,
                "timestamp": request.timestamp
            }
        )
        
        # Process video assistance request
        response = await agent_router.handle_video_assistance(request)
        
        # Log response
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="agent8",
            request_data=request.dict(),
            response_data=response.dict(),
            success=True,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in video assistance endpoint: {str(e)}")
        
        # Log error
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="agent8",
            request_data=request.dict(),
            response_data={"error": str(e)},
            success=False,
            response_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error providing video assistance: {str(e)}"
        )
