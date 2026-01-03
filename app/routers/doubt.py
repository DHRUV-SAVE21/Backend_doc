from fastapi import APIRouter, HTTPException
from app.services.agent_router import agent_router
from app.services.n8n_client import n8n_client
from app.schemas.requests import DoubtRequest
from app.schemas.responses import DoubtResponse, ErrorResponse
from app.models.mongodb import mongodb_service
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["doubt"])


@router.post("/doubt", response_model=DoubtResponse)
async def resolve_doubt(request: DoubtRequest):
    """
    FEATURE 1: Live Doubt Resolution
    
    Direct doubt resolution using Agent 1.
    Provides immediate solutions to student questions.
    
    Example Postman Request:
    POST http://localhost:8000/api/doubt
    {
        "user_id": "u123",
        "question_id": "q101",
        "step_number": 1,
        "student_answer": "I don't understand binary search",
        "intent": "direct_solution",
        "topic": "Binary Search",
        "difficulty": "medium"
    }
    """
    start_time = time.time()
    
    try:
        # Log incoming request
        await mongodb_service.log_user_activity(
            user_id=request.user_id,
            activity_data={
                "activity_type": "doubt_resolution",
                "question_id": request.question_id,
                "topic": request.topic,
                "difficulty": request.difficulty.value,
                "intent": request.intent.value
            }
        )
        
        # Process doubt resolution
        response = await agent_router.handle_doubt_resolution(request)
        
        # Log agent response
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="agent1",
            request_data=request.dict(),
            response_data=response.dict(),
            success=True,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in doubt resolution endpoint: {str(e)}")
        
        # Log error
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="agent1",
            request_data=request.dict(),
            response_data={"error": str(e)},
            success=False,
            response_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing doubt: {str(e)}"
        )
