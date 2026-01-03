from fastapi import APIRouter, HTTPException
from app.services.agent_router import agent_router
from app.schemas.requests import ProgressRequest
from app.schemas.responses import ProgressResponse, ErrorResponse
from app.models.mongodb import mongodb_service
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["progress"])


@router.post("/progress", response_model=ProgressResponse)
async def get_progress(request: ProgressRequest):
    """
    FEATURE 4: Self-Improving System - Progress Tracking
    
    Provides comprehensive progress tracking using Agents 6 and 7.
    Includes mastery levels, learning velocity, and personalized recommendations.
    
    Example Postman Request:
    POST http://localhost:8000/api/progress
    {
        "user_id": "u123",
        "topic": "Binary Search",
        "time_range": 7
    }
    """
    start_time = time.time()
    
    try:
        # Log incoming request
        await mongodb_service.log_user_activity(
            user_id=request.user_id,
            activity_data={
                "activity_type": "progress_tracking",
                "topic": request.topic,
                "time_range": request.time_range
            }
        )
        
        # Process progress tracking
        response = await agent_router.handle_progress_tracking(request)
        
        # Store learning insights
        await mongodb_service.store_learning_insights(
            user_id=request.user_id,
            insights={
                "strengths": response.strengths,
                "weaknesses": response.weaknesses,
                "recommendations": response.recommendations,
                "progress_data": response.progress_data
            }
        )
        
        # Log response
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="agent6",
            request_data=request.dict(),
            response_data=response.dict(),
            success=True,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in progress tracking endpoint: {str(e)}")
        
        # Log error
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="agent6",
            request_data=request.dict(),
            response_data={"error": str(e)},
            success=False,
            response_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error tracking progress: {str(e)}"
        )
