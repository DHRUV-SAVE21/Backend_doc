from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDBService:
    def __init__(self):
        self.client = None
        self.database = None
        self.db_name = settings.MONGODB_DATABASE
        
    async def connect(self):
        """Initialize MongoDB connection"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client[self.db_name]
            
            # Test connection
            await self.database.command('ping')
            logger.info("Connected to MongoDB successfully")
            
            # Create indexes for better performance
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create necessary indexes"""
        try:
            # User activity logs index
            await self.database.user_activity.create_index([
                ("user_id", 1),
                ("timestamp", -1)
            ])
            
            # Agent response logs index
            await self.database.agent_responses.create_index([
                ("user_id", 1),
                ("agent_name", 1),
                ("timestamp", -1)
            ])
            
            # Analytics index
            await self.database.analytics.create_index([
                ("user_id", 1),
                ("date", -1)
            ])
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {str(e)}")
    
    async def log_user_activity(self, user_id: str, activity_data: Dict[str, Any]):
        """Log user activity"""
        try:
            activity = {
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                **activity_data
            }
            
            await self.database.user_activity.insert_one(activity)
            logger.debug(f"Logged activity for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to log user activity: {str(e)}")
    
    async def log_agent_response(
        self, 
        user_id: str, 
        agent_name: str, 
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        success: bool,
        response_time: float
    ):
        """Log agent response for analytics"""
        try:
            log_entry = {
                "user_id": user_id,
                "agent_name": agent_name,
                "timestamp": datetime.utcnow(),
                "request_data": request_data,
                "response_data": response_data,
                "success": success,
                "response_time_ms": response_time * 1000,
                "date": datetime.utcnow().date()
            }
            
            await self.database.agent_responses.insert_one(log_entry)
            logger.debug(f"Logged agent response for {agent_name}")
            
        except Exception as e:
            logger.error(f"Failed to log agent response: {str(e)}")
    
    async def get_user_analytics(
        self, 
        user_id: str, 
        days: int = 7
    ) -> Dict[str, Any]:
        """Get user analytics for the specified period"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Aggregate user activity
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                            "activity_type": "$activity_type"
                        },
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$group": {
                        "_id": "$_id.date",
                        "activities": {
                            "$push": {
                                "type": "$_id.activity_type",
                                "count": "$count"
                            }
                        },
                        "total": {"$sum": "$count"}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            daily_activity = await self.database.user_activity.aggregate(pipeline).to_list(length=None)
            
            # Agent performance analytics
            agent_pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$agent_name",
                        "total_calls": {"$sum": 1},
                        "successful_calls": {
                            "$sum": {"$cond": [{"$eq": ["$success", True]}, 1, 0]}
                        },
                        "avg_response_time": {"$avg": "$response_time_ms"}
                    }
                }
            ]
            
            agent_performance = await self.database.agent_responses.aggregate(agent_pipeline).to_list(length=None)
            
            return {
                "daily_activity": daily_activity,
                "agent_performance": agent_performance,
                "period_days": days,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {str(e)}")
            return {}
    
    async def get_progress_metrics(
        self, 
        user_id: str, 
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get progress metrics for a user"""
        try:
            match_query = {"user_id": user_id}
            if topic:
                match_query["topic"] = topic
            
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": "$topic",
                        "total_attempts": {"$sum": 1},
                        "successful_attempts": {
                            "$sum": {"$cond": [{"$eq": ["$success", True]}, 1, 0]}
                        },
                        "avg_stuck_score": {"$avg": "$stuck_score"},
                        "hints_used": {"$sum": "$hints_used"},
                        "last_activity": {"$max": "$timestamp"}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            progress_data = await self.database.user_activity.aggregate(pipeline).to_list(length=None)
            
            # Calculate overall metrics
            total_attempts = sum(item["total_attempts"] for item in progress_data)
            total_successful = sum(item["successful_attempts"] for item in progress_data)
            overall_success_rate = (total_successful / total_attempts * 100) if total_attempts > 0 else 0
            
            return {
                "topic_progress": progress_data,
                "overall_metrics": {
                    "total_attempts": total_attempts,
                    "successful_attempts": total_successful,
                    "success_rate": overall_success_rate,
                    "topics_studied": len(progress_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get progress metrics: {str(e)}")
            return {}
    
    async def store_learning_insights(
        self, 
        user_id: str, 
        insights: Dict[str, Any]
    ):
        """Store learning insights and recommendations"""
        try:
            insight_doc = {
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "insights": insights,
                "type": "learning_insight"
            }
            
            await self.database.learning_insights.insert_one(insight_doc)
            logger.debug(f"Stored learning insights for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to store learning insights: {str(e)}")
    
    async def get_recent_activity(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent user activity"""
        try:
            activities = await self.database.user_activity.find(
                {"user_id": user_id}
            ).sort("timestamp", DESCENDING).limit(limit).to_list(length=None)
            
            # Convert ObjectId to string for JSON serialization
            for activity in activities:
                activity["_id"] = str(activity["_id"])
                if "timestamp" in activity:
                    activity["timestamp"] = activity["timestamp"].isoformat()
            
            return activities
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {str(e)}")
            return []


# Global instance
mongodb_service = MongoDBService()
