from fastapi import APIRouter, HTTPException
from app.services.agent_router import agent_router
from app.schemas.requests import ProblemSolveRequest, HintRequest
from app.schemas.responses import ProblemSolveResponse, HintResponse, ErrorResponse
from app.models.mongodb import mongodb_service
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/problem", tags=["problem"])


@router.post("/solve", response_model=ProblemSolveResponse)
async def solve_problem(request: ProblemSolveRequest):
    """
    FEATURE 2: Guided Problem Solving
    
    Orchestrates multiple agents for guided problem solving with hints.
    Uses Agents 2, 3, 4, and potentially 8 for comprehensive assistance.
    
    Example Postman Request:
    POST http://localhost:8000/api/problem/solve
    {
        "user_id": "u123",
        "question_id": "q101",
        "step_number": 2,
        "student_answer": "I'm stuck at the recursion step",
        "intent": "guided",
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
                "activity_type": "problem_solving",
                "question_id": request.question_id,
                "step_number": request.step_number,
                "topic": request.topic,
                "difficulty": request.difficulty.value,
                "intent": request.intent.value
            }
        )
        
        # Process problem solving
        response = await agent_router.handle_guided_problem_solving(request)
        
        # Log response
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="agent_router",
            request_data=request.dict(),
            response_data=response.dict(),
            success=True,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in problem solving endpoint: {str(e)}")
        
        # Log error
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="agent_router",
            request_data=request.dict(),
            response_data={"error": str(e)},
            success=False,
            response_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error solving problem: {str(e)}"
        )


@router.post("/hint", response_model=HintResponse)
async def get_hint(request: HintRequest):
    """
    Progressive hint system for problem solving.
    Provides leveled hints using Agent 2.
    
    Example Postman Request:
    POST http://localhost:8000/api/problem/hint
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
    """
    start_time = time.time()
    
    try:
        # Log incoming request
        await mongodb_service.log_user_activity(
            user_id=request.user_id,
            activity_data={
                "activity_type": "hint_request",
                "question_id": request.question_id,
                "current_hint_level": request.current_hint_level,
                "topic": request.topic,
                "difficulty": request.difficulty.value
            }
        )
        
        # Process hint request
        response = await agent_router.handle_hint_request(request)
        
        # Log response
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="agent2",
            request_data=request.dict(),
            response_data=response.dict(),
            success=True,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in hint endpoint: {str(e)}")
        
        # Log error
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="agent2",
            request_data=request.dict(),
            response_data={"error": str(e)},
            success=False,
            response_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error providing hint: {str(e)}"
        )


@router.post("/progress", response_model=ProblemSolveResponse)
async def update_problem_progress(request: ProblemSolveRequest):
    """
    Update problem solving progress and analytics.
    Tracks user progress through problem solving steps.
    
    Example Postman Request:
    POST http://localhost:8000/api/problem/progress
    {
        "user_id": "u123",
        "question_id": "q101",
        "step_number": 3,
        "student_answer": "I think I need to check mid element",
        "intent": "guided",
        "topic": "Binary Search",
        "difficulty": "medium"
    }
    """
    start_time = time.time()
    
    try:
        # Log progress update
        await mongodb_service.log_user_activity(
            user_id=request.user_id,
            activity_data={
                "activity_type": "progress_update",
                "question_id": request.question_id,
                "step_number": request.step_number,
                "topic": request.topic,
                "difficulty": request.difficulty.value,
                "student_answer": request.student_answer
            }
        )
        
        # Process progress update using guided problem solving logic
        response = await agent_router.handle_guided_problem_solving(request)
        
        # Log response
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="progress_tracker",
            request_data=request.dict(),
            response_data=response.dict(),
            success=True,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in progress endpoint: {str(e)}")
        
        # Log error
        response_time = time.time() - start_time
        await mongodb_service.log_agent_response(
            user_id=request.user_id,
            agent_name="progress_tracker",
            request_data=request.dict(),
            response_data={"error": str(e)},
            success=False,
            response_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error updating progress: {str(e)}"
        )
