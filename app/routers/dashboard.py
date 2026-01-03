from fastapi import APIRouter, HTTPException
from app.services.agent_router import agent_router
from app.schemas.requests import DashboardRequest
from app.schemas.responses import DashboardResponse, ErrorResponse
from app.models.mongodb import mongodb_service
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(user_id: str, topic: str = None):
    """
    FEATURE 5: Progress & Revision - Dashboard with Flashcards
    
    Comprehensive dashboard showing user progress, analytics, and flashcard recommendations.
    Uses Agents 6 and 7 for progress tracking and flashcard generation.
    
    Example Postman Request:
    GET http://localhost:8000/api/dashboard?user_id=u123&topic=Binary%20Search
    
    Or without topic filter:
    GET http://localhost:8000/api/dashboard?user_id=u123
    """
    start_time = time.time()
    
    try:
        # Create dashboard request
        dashboard_request = DashboardRequest(user_id=user_id)
        
        # Log incoming request
        await mongodb_service.log_user_activity(
            user_id=user_id,
            activity_data={
                "activity_type": "dashboard_view",
                "topic_filter": topic,
                "request_type": "GET"
            }
        )
        
        # Process dashboard generation
        response = await agent_router.handle_dashboard(dashboard_request)
        
        # Apply topic filter if specified
        if topic and response.progress_summary:
            # Filter progress summary by topic
            if "strengths" in response.progress_summary:
                response.progress_summary["strengths"] = [
                    t for t in response.progress_summary["strengths"] 
                    if topic.lower() in t.lower()
                ]
            if "weaknesses" in response.progress_summary:
                response.progress_summary["weaknesses"] = [
                    t for t in response.progress_summary["weaknesses"] 
                    if topic.lower() in t.lower()
                ]
        
        # Get additional analytics from MongoDB
        analytics_data = await mongodb_service.get_user_analytics(user_id, days=30)
        recent_activity = await mongodb_service.get_recent_activity(user_id, limit=5)
        
        # Enhance response with MongoDB data
        response.analytics.update({
            "mongodb_analytics": analytics_data,
            "recent_activity": recent_activity,
            "data_sources": ["n8n_agents", "mongodb"]
        })
        
        # Log response
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=user_id,
            agent_name="dashboard",
            request_data={"user_id": user_id, "topic": topic},
            response_data=response.dict(),
            success=True,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in dashboard endpoint: {str(e)}")
        
        # Log error
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=user_id,
            agent_name="dashboard",
            request_data={"user_id": user_id, "topic": topic},
            response_data={"error": str(e)},
            success=False,
            response_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error generating dashboard: {str(e)}"
        )


@router.post("/dashboard", response_model=DashboardResponse)
async def create_dashboard(request: DashboardRequest):
    """
    Alternative POST endpoint for dashboard generation.
    Useful when additional parameters need to be sent in request body.
    
    Example Postman Request:
    POST http://localhost:8000/api/dashboard
    {
        "user_id": "u123"
    }
    """
    start_time = time.time()
    
    try:
        # Log incoming request
        await mongodb_service.log_user_activity(
            user_id=request.user_id,
            activity_data={
                "activity_type": "dashboard_view",
                "request_type": "POST"
            }
        )
        
        # Process dashboard generation
        response = await agent_router.handle_dashboard(request)
        
        # Log response
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="dashboard",
            request_data=request.dict(),
            response_data=response.dict(),
            success=True,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in dashboard POST endpoint: {str(e)}")
        
        # Log error
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="dashboard",
            request_data=request.dict(),
            response_data={"error": str(e)},
            success=False,
            response_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error generating dashboard: {str(e)}"
        )
