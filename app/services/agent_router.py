from typing import Dict, Any, Optional, List
import asyncio
from app.services.n8n_client import n8n_client
from app.schemas.agent_schemas import *
from app.schemas.responses import *
from app.schemas.requests import *
import logging

logger = logging.getLogger(__name__)


class AgentRouter:
    """
    Central decision engine that orchestrates all 8 AI agents
    """
    
    def __init__(self):
        self.max_hint_levels = 4
        self.stuck_threshold = 70
        self.hesitation_threshold = 0.7
        
    async def handle_doubt_resolution(self, request: DoubtRequest) -> DoubtResponse:
        """
        FEATURE 1: Live Doubt Resolution
        Direct solution for student doubts
        """
        try:
            # Call Agent 1 for direct doubt resolution
            agent_request = Agent1Request(
                user_id=request.user_id,
                question_id=request.question_id,
                student_answer=request.student_answer,
                topic=request.topic,
                difficulty=request.difficulty.value
            )
            
            agent_response = await n8n_client.call_agent1_direct_doubt(agent_request)
            
            if not agent_response.success:
                return DoubtResponse(
                    mode="SOLUTION",
                    content=f"Error resolving doubt: {agent_response.error}",
                    analytics={"error": True, "agent": "agent1"}
                )
            
            # Extract solution from agent response
            solution_data = agent_response.data
            content = solution_data.get("solution", "Solution not available")
            confidence = solution_data.get("confidence", 0.0)
            
            return DoubtResponse(
                mode="SOLUTION",
                content=content,
                confidence_score=confidence,
                analytics={
                    "agent": "agent1",
                    "confidence": confidence,
                    "topic": request.topic,
                    "difficulty": request.difficulty.value
                }
            )
            
        except Exception as e:
            logger.error(f"Error in doubt resolution: {str(e)}")
            return DoubtResponse(
                mode="SOLUTION",
                content=f"Error processing doubt: {str(e)}",
                analytics={"error": True, "exception": str(e)}
            )
    
    async def handle_guided_problem_solving(self, request: ProblemSolveRequest) -> ProblemSolveResponse:
        """
        FEATURE 2: Guided Problem Solving with 4-level hints
        """
        try:
            # Parallel execution for efficiency
            tasks = []
            
            # Agent 3: Hesitation Detection
            hesitation_request = Agent3Request(
                user_id=request.user_id,
                question_id=request.question_id,
                step_number=request.step_number,
                student_answer=request.student_answer
            )
            tasks.append(n8n_client.call_agent3_hesitation_detector(hesitation_request))
            
            # Agent 4: Stuck Score Calculation
            stuck_request = Agent4Request(
                user_id=request.user_id,
                question_id=request.question_id,
                step_number=request.step_number,
                student_answer=request.student_answer,
                hint_level=0
            )
            tasks.append(n8n_client.call_agent4_stuck_score(stuck_request))
            
            # Execute parallel calls
            hesitation_response, stuck_response = await asyncio.gather(*tasks)
            
            # Analyze responses
            hesitation_data = hesitation_response.data if hesitation_response.success else {}
            stuck_data = stuck_response.data if stuck_response.success else {}
            
            stuck_score = stuck_data.get("stuck_score", 0)
            hesitation_detected = hesitation_data.get("hesitation_detected", False)
            
            # Determine if video assistance is needed
            video_needed = (
                stuck_score >= self.stuck_threshold or
                hesitation_data.get("prolonged_hesitation", False) or
                request.intent == UserIntent.VIDEO
            )
            
            if video_needed:
                video_response = await self._trigger_video_assistance(
                    request, "high_stuck_or_hesitation", {
                        "stuck_score": stuck_score,
                        "hesitation_detected": hesitation_detected
                    }
                )
                
                if video_response.success:
                    video_data = video_response.data
                    return ProblemSolveResponse(
                        mode="VIDEO",
                        content=video_data.get("explanation", "Video assistance triggered"),
                        analytics={
                            "video_triggered": True,
                            "stuck_score": stuck_score,
                            "hesitation": hesitation_detected,
                            "agent": "agent8"
                        }
                    )
            
            # Get hint from Agent 2
            hint_request = Agent2Request(
                user_id=request.user_id,
                question_id=request.question_id,
                current_hint_level=1,
                student_answer=request.student_answer,
                topic=request.topic,
                difficulty=request.difficulty.value
            )
            
            hint_response = await n8n_client.call_agent2_hint_strategy(hint_request)
            
            if hint_response.success:
                hint_data = hint_response.data
                return ProblemSolveResponse(
                    mode="HINT",
                    content=hint_data.get("hint", "Hint not available"),
                    hint_level=hint_data.get("hint_level", 1),
                    stuck_score=stuck_score,
                    analytics={
                        "agent": "agent2",
                        "hint_level": hint_data.get("hint_level", 1),
                        "stuck_score": stuck_score
                    }
                )
            else:
                return ProblemSolveResponse(
                    mode="SOLUTION",
                    content="Unable to provide hint at this time.",
                    analytics={"error": True, "agent": "agent2"}
                )
                
        except Exception as e:
            logger.error(f"Error in guided problem solving: {str(e)}")
            return ProblemSolveResponse(
                mode="SOLUTION",
                content=f"Error in problem solving: {str(e)}",
                analytics={"error": True, "exception": str(e)}
            )
    
    async def handle_hint_request(self, request: HintRequest) -> HintResponse:
        """
        Handle progressive hint requests
        """
        try:
            current_level = request.current_hint_level + 1
            
            if current_level > self.max_hint_levels:
                # Max hints reached, trigger video assistance
                video_response = await self._trigger_video_assistance(
                    request, "hints_exhausted", {"hint_level": current_level}
                )
                
                if video_response.success:
                    video_data = video_response.data
                    return HintResponse(
                        mode="VIDEO",
                        content=video_data.get("explanation", "Video assistance triggered"),
                        hint_level=current_level,
                        next_hint_available=False,
                        analytics={"video_triggered": True, "hints_exhausted": True}
                    )
            
            # Get hint from Agent 2
            hint_request = Agent2Request(
                user_id=request.user_id,
                question_id=request.question_id,
                current_hint_level=current_level,
                student_answer=request.student_answer,
                topic=request.topic,
                difficulty=request.difficulty.value
            )
            
            hint_response = await n8n_client.call_agent2_hint_strategy(hint_request)
            
            if hint_response.success:
                hint_data = hint_response.data
                return HintResponse(
                    mode="HINT",
                    content=hint_data.get("hint", "Hint not available"),
                    hint_level=hint_data.get("hint_level", current_level),
                    next_hint_available=hint_data.get("next_available", current_level < self.max_hint_levels),
                    analytics={
                        "agent": "agent2",
                        "hint_level": hint_data.get("hint_level", current_level)
                    }
                )
            else:
                return HintResponse(
                    mode="HINT",
                    content="Unable to provide hint at this time.",
                    hint_level=current_level,
                    next_hint_available=False,
                    analytics={"error": True, "agent": "agent2"}
                )
                
        except Exception as e:
            logger.error(f"Error in hint request: {str(e)}")
            return HintResponse(
                mode="HINT",
                content=f"Error providing hint: {str(e)}",
                hint_level=request.current_hint_level,
                next_hint_available=False,
                analytics={"error": True, "exception": str(e)}
            )
    
    async def handle_video_assistance(self, request: VideoAssistRequest) -> VideoAssistResponse:
        """
        FEATURE 3: Adaptive Video Assistance
        """
        try:
            video_response = await self._trigger_video_assistance(
                request, "user_request", {
                    "video_context": request.video_context,
                    "timestamp": request.timestamp
                }
            )
            
            if video_response.success:
                video_data = video_response.data
                return VideoAssistResponse(
                    mode="VIDEO",
                    content=video_data.get("explanation", "Video assistance provided"),
                    video_ref=video_data.get("video_ref"),
                    youtube_metadata=video_data.get("youtube_metadata"),
                    action=video_data.get("action", "SHOW_YOUTUBE"),
                    analytics={
                        "agent": "agent8",
                        "action": video_data.get("action", "SHOW_YOUTUBE")
                    }
                )
            else:
                return VideoAssistResponse(
                    mode="VIDEO",
                    content=f"Unable to provide video assistance: {video_response.error}",
                    action="ERROR",
                    analytics={"error": True, "agent": "agent8"}
                )
                
        except Exception as e:
            logger.error(f"Error in video assistance: {str(e)}")
            return VideoAssistResponse(
                mode="VIDEO",
                content=f"Error in video assistance: {str(e)}",
                action="ERROR",
                analytics={"error": True, "exception": str(e)}
            )
    
    async def handle_progress_tracking(self, request: ProgressRequest) -> ProgressResponse:
        """
        FEATURE 4: Self-Improving System - Progress Tracking
        """
        try:
            # Call Agent 6 for progress tracking
            progress_request = Agent6Request(
                user_id=request.user_id,
                topic=request.topic,
                time_range=request.time_range
            )
            
            progress_response = await n8n_client.call_agent6_progress_tracker(progress_request)
            
            if not progress_response.success:
                return ProgressResponse(
                    user_id=request.user_id,
                    progress_data={},
                    analytics={"error": True, "agent": "agent6"}
                )
            
            progress_data = progress_response.data
            
            # Get flashcard recommendations from Agent 7
            flashcard_request = Agent7Request(
                user_id=request.user_id,
                topic=request.topic
            )
            
            flashcard_response = await n8n_client.call_agent7_flashcard_recommender(flashcard_request)
            
            flashcards = []
            if flashcard_response.success:
                flashcard_data = flashcard_response.data
                flashcards = flashcard_data.get("flashcards", [])
            
            # Analyze strengths and weaknesses
            mastery_levels = progress_data.get("mastery_levels", {})
            strengths = [topic for topic, level in mastery_levels.items() if level >= 0.8]
            weaknesses = [topic for topic, level in mastery_levels.items() if level < 0.5]
            
            # Generate recommendations
            recommendations = []
            if weaknesses:
                recommendations.append(f"Focus on weak topics: {', '.join(weaknesses[:3])}")
            if flashcards:
                recommendations.append(f"Review {len(flashcards)} recommended flashcards")
            
            return ProgressResponse(
                user_id=request.user_id,
                progress_data=progress_data,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                analytics={
                    "agent": "agent6",
                    "mastery_count": len(strengths),
                    "weakness_count": len(weaknesses),
                    "flashcard_count": len(flashcards)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in progress tracking: {str(e)}")
            return ProgressResponse(
                user_id=request.user_id,
                progress_data={},
                analytics={"error": True, "exception": str(e)}
            )
    
    async def handle_dashboard(self, request: DashboardRequest) -> DashboardResponse:
        """
        FEATURE 5: Progress & Revision - Dashboard with Flashcards
        """
        try:
            # Get comprehensive progress data
            progress_request = Agent6Request(
                user_id=request.user_id,
                time_range=30  # Last 30 days
            )
            
            progress_response = await n8n_client.call_agent6_progress_tracker(progress_request)
            
            # Get flashcard recommendations
            flashcard_request = Agent7Request(
                user_id=request.user_id
            )
            
            flashcard_response = await n8n_client.call_agent7_flashcard_recommender(flashcard_request)
            
            # Process responses
            progress_data = progress_response.data if progress_response.success else {}
            flashcard_data = flashcard_response.data if flashcard_response.success else {}
            
            # Create dashboard overview
            overview = {
                "total_time_spent": progress_data.get("time_spent", 0),
                "learning_velocity": progress_data.get("learning_velocity", 0),
                "mastery_average": self._calculate_average_mastery(progress_data.get("mastery_levels", {})),
                "questions_attempted": progress_data.get("questions_attempted", 0)
            }
            
            # Progress summary
            progress_summary = {
                "strengths": [topic for topic, level in progress_data.get("mastery_levels", {}).items() if level >= 0.8],
                "weaknesses": [topic for topic, level in progress_data.get("mastery_levels", {}).items() if level < 0.5],
                "recent_topics": progress_data.get("recent_topics", []),
                "improvement_rate": progress_data.get("improvement_rate", 0)
            }
            
            return DashboardResponse(
                user_id=request.user_id,
                overview=overview,
                recent_activity=progress_data.get("recent_activity", []),
                progress_summary=progress_summary,
                flashcard_recommendations=flashcard_data.get("flashcards", []),
                analytics={
                    "agents": ["agent6", "agent7"],
                    "data_freshness": "real-time"
                }
            )
            
        except Exception as e:
            logger.error(f"Error in dashboard generation: {str(e)}")
            return DashboardResponse(
                user_id=request.user_id,
                overview={},
                progress_summary={},
                analytics={"error": True, "exception": str(e)}
            )
    
    async def _trigger_video_assistance(
        self, 
        request, 
        trigger_reason: str, 
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        Internal method to trigger Agent 8 (Video Intelligence)
        """
        video_request = Agent8Request(
            user_id=request.user_id,
            question_id=request.question_id,
            topic=request.topic,
            trigger_reason=trigger_reason,
            context=context
        )
        
        return await n8n_client.call_agent8_video_intelligence(video_request)
    
    def _calculate_average_mastery(self, mastery_levels: Dict[str, float]) -> float:
        """Calculate average mastery level across all topics"""
        if not mastery_levels:
            return 0.0
        return sum(mastery_levels.values()) / len(mastery_levels)


# Global instance
agent_router = AgentRouter()
