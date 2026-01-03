import httpx
import asyncio
from typing import Dict, Any, Optional
from app.schemas.responses import AgentResponse
from app.schemas.agent_schemas import *
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class N8NClient:
    def __init__(self):
        self.base_url = settings.N8N_BASE_URL
        self.timeout = settings.N8N_TIMEOUT
        self.max_retries = settings.N8N_MAX_RETRIES
        
    async def _make_request(
        self, 
        webhook_path: str, 
        data: Dict[str, Any],
        agent_name: str
    ) -> AgentResponse:
        """
        Make async HTTP request to n8n webhook with retry logic
        """
        url = f"{self.base_url}{webhook_path}"
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        url,
                        json=data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        return AgentResponse(
                            success=True,
                            data=response.json(),
                            agent_name=agent_name
                        )
                    else:
                        logger.error(f"Agent {agent_name} failed with status {response.status_code}")
                        if attempt == self.max_retries - 1:
                            return AgentResponse(
                                success=False,
                                error=f"HTTP {response.status_code}: {response.text}",
                                agent_name=agent_name
                            )
                        
            except httpx.TimeoutException:
                logger.error(f"Timeout calling agent {agent_name}, attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    return AgentResponse(
                        success=False,
                        error="Request timeout",
                        agent_name=agent_name
                    )
                    
            except Exception as e:
                logger.error(f"Error calling agent {agent_name}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return AgentResponse(
                        success=False,
                        error=f"Connection error: {str(e)}",
                        agent_name=agent_name
                    )
                
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return AgentResponse(
            success=False,
            error="Max retries exceeded",
            agent_name=agent_name
        )

    async def call_agent1_direct_doubt(self, request: Agent1Request) -> AgentResponse:
        """Agent 1 – Direct Doubt Resolver"""
        return await self._make_request(
            "/webhook/agent1/submit-doubt",
            request.dict(),
            "Direct Doubt Resolver"
        )

    async def call_agent2_hint_strategy(self, request: Agent2Request) -> AgentResponse:
        """Agent 2 – Hint Strategy Agent"""
        return await self._make_request(
            "/webhook/agent2/get-hint",
            request.dict(),
            "Hint Strategy Agent"
        )

    async def call_agent3_hesitation_detector(self, request: Agent3Request) -> AgentResponse:
        """Agent 3 – Hesitation Detector"""
        return await self._make_request(
            "/webhook/agent3/hesitation",
            request.dict(),
            "Hesitation Detector"
        )

    async def call_agent4_stuck_score(self, request: Agent4Request) -> AgentResponse:
        """Agent 4 – Stuck Score Calculator"""
        return await self._make_request(
            "/webhook/agent4/stuck-score",
            request.dict(),
            "Stuck Score Calculator"
        )

    async def call_agent5_mistake_pattern(self, request: Agent5Request) -> AgentResponse:
        """Agent 5 – Mistake Pattern Learner"""
        return await self._make_request(
            "/webhook/agent5/mistake-pattern",
            request.dict(),
            "Mistake Pattern Learner"
        )

    async def call_agent6_progress_tracker(self, request: Agent6Request) -> AgentResponse:
        """Agent 6 – Progress Tracker"""
        return await self._make_request(
            "/webhook/agent6/progress",
            request.dict(),
            "Progress Tracker"
        )

    async def call_agent7_flashcard_recommender(self, request: Agent7Request) -> AgentResponse:
        """Agent 7 – Flashcard Recommender"""
        return await self._make_request(
            "/webhook/agent7/flashcards",
            request.dict(),
            "Flashcard Recommender"
        )

    async def call_agent8_video_intelligence(self, request: Agent8Request) -> AgentResponse:
        """Agent 8 – Video Intelligence Agent"""
        return await self._make_request(
            "/webhook/agent8/video-intelligence",
            request.dict(),
            "Video Intelligence Agent"
        )


# Global instance
n8n_client = N8NClient()
