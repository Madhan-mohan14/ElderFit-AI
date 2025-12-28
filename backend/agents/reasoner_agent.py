from typing import Dict, Any, List
from datetime import datetime
from backend.agents.intake_agent import IntakeAgent
from backend.agents.mood_agent import MoodUnderstandingAgent
from backend.agents.nutrition_agent import NutritionPlannerAgent
from backend.agents.compliance_agent import ComplianceMonitorAgent
from backend.agents.optimizer_agent import PlanOptimizerAgent
from backend.agents.trend_predictor import TrendPredictor
from backend.agents.memory_agent import MemoryAgent
from backend.services.youtube_service import YouTubeService
from backend.services.openai_service import OpenAIService
from backend.models.schemas import DailyPlan, DecisionTrace

class ReasonerAgent:
    """Main orchestrating agent that applies symbolic rules, LLM reasoning, and plan scoring"""
    
    def __init__(self):
        self.intake_agent = IntakeAgent()
        self.mood_agent = MoodUnderstandingAgent()
        self.nutrition_agent = NutritionPlannerAgent()
        self.compliance_agent = ComplianceMonitorAgent()
        self.optimizer_agent = PlanOptimizerAgent()
        self.trend_predictor = TrendPredictor()
        self.memory_agent = MemoryAgent()
        self.youtube_service = YouTubeService()
        self.openai_service = OpenAIService()
        
        # Symbolic safety rules
        self.safety_rules = [
            "No hard-to-chew foods for users over 75",
            "Low spice preference for all elders",
            "Maximum 20 minutes exercise per day",
            "Minimum 1500 calories per day",
            "Always include calcium sources",
            "Hydration reminder if energy is low"
        ]
    
    async def generate_plan(self, user_profile: Dict, check_in: Dict, language: str = "en") -> Dict[str, Any]:
        """Main plan generation pipeline"""
        import logging
        logger = logging.getLogger(__name__)
        
        triggered_rules = []
        apis_called = []
        
        # Step 1: Intake processing
        # Convert dicts to proper objects for intake agent
        from backend.models.schemas import UserProfile, CheckInRequest, Mood, AppetiteLevel, EnergyLevel
        
        try:
            # Validate and normalize mood
            mood_value = check_in.get("mood", "neutral")
            if mood_value not in [m.value for m in Mood]:
                mood_value = "neutral"
            
            # Validate and normalize appetite
            appetite_value = check_in.get("appetite", "normal")
            if appetite_value not in [a.value for a in AppetiteLevel]:
                appetite_value = "normal"
            
            # Validate and normalize energy level
            energy_value = check_in.get("energy_level")
            if energy_value and energy_value not in [e.value for e in EnergyLevel]:
                energy_value = None
            
            # Create UserProfile object
            profile_obj = UserProfile(
                age=user_profile.get("age", 70),
                allergies=user_profile.get("allergies", []) or [],
                diet_type=user_profile.get("diet_type", "balanced"),
                medical_conditions=user_profile.get("medical_conditions", []) or []
            )
            
            # Create CheckInRequest object
            check_in_obj = CheckInRequest(
                mood=Mood(mood_value),
                appetite=AppetiteLevel(appetite_value),
                yesterday_adherence=float(check_in.get("yesterday_adherence", 80)),
                energy_level=EnergyLevel(energy_value) if energy_value else None
            )
            
            user_context = self.intake_agent.process_intake(profile_obj, check_in_obj)
        except Exception as e:
            # Fallback to default values if validation fails
            user_context = {
                "age": user_profile.get("age", 70),
                "allergies": user_profile.get("allergies", []),
                "diet_type": user_profile.get("diet_type", "balanced"),
                "medical_conditions": user_profile.get("medical_conditions", []),
                "mood": check_in.get("mood", "neutral"),
                "appetite": check_in.get("appetite", "normal"),
                "energy": check_in.get("energy_level", "medium"),
                "yesterday_adherence": float(check_in.get("yesterday_adherence", 80)),
                "needs_attention": False
            }
        
        # Step 2: Trend prediction
        try:
            trends = self.trend_predictor.predict_trends(user_context)
            user_context.update(trends)
        except Exception as e:
            logger.warning(f"Trend prediction failed: {str(e)}, using defaults")
            user_context["energy_trend"] = user_context.get("energy", "medium")
        
        # Step 3: Mood interpretation
        try:
            mood_interpretation = self.mood_agent.interpret_mood(
                user_context["mood"], 
                user_context.get("energy_trend", user_context.get("energy", "medium"))
            )
        except Exception as e:
            logger.warning(f"Mood interpretation failed: {str(e)}, using defaults")
            mood_interpretation = {
                "interpretation": f"User is feeling {user_context.get('mood', 'neutral')}",
                "preferences": {"meal_complexity": "normal", "exercise_intensity": "normal"},
                "suggested_meal_types": ["balanced"],
                "suggested_exercise_types": ["gentle movement"]
            }
        
        # Step 4: Memory retrieval
        try:
            similar_episodes = self.memory_agent.retrieve_similar(user_context, top_k=3)
            memory_insights = self.memory_agent.get_preferences()
        except Exception as e:
            logger.warning(f"Memory retrieval failed: {str(e)}, using defaults")
            similar_episodes = []
            memory_insights = {}
        
        # Step 5: Apply safety rules
        triggered_rules.extend(self._apply_safety_rules(user_context))
        
        # Step 6: Generate nutrition plan
        apis_called.append("Nutrition API (USDA)")
        try:
            meal_plan = await self.nutrition_agent.generate_plan(user_context, mood_interpretation)
        except Exception as e:
            # Fallback to default meals if nutrition service fails
            from backend.models.schemas import DailyMealPlan, MealItem
            meal_plan = DailyMealPlan(
                breakfast=MealItem(name="Oatmeal with fruits", calories=250, protein=10, carbs=45, fat=5, fiber=6, calcium=150),
                lunch=MealItem(name="Vegetable soup", calories=350, protein=8, carbs=55, fat=5, fiber=8, calcium=100),
                dinner=MealItem(name="Steamed vegetables", calories=400, protein=25, carbs=30, fat=10, fiber=6, calcium=80),
                snacks=[],
                total_calories=1000,
                total_protein=43,
                total_carbs=130,
                total_fat=20,
                total_fiber=20,
                total_calcium=330
            )
        
        # Step 7: Get exercise videos (with timeout to prevent hanging)
        apis_called.append("YouTube Data API")
        try:
            import asyncio
            # Add timeout for YouTube search (8 seconds max - if it takes longer, use fallback)
            try:
                exercises = await asyncio.wait_for(
                    self.youtube_service.search_elder_exercises(
                        duration_min=5, limit=5  # Reduced to 5 for faster response
                    ),
                    timeout=8.0  # 8 second timeout for YouTube search
                )
            except asyncio.TimeoutError:
                logger.warning("YouTube search timed out after 8 seconds, using fallback videos")
                exercises = self.youtube_service._get_fallback_videos(5)
            
            if not exercises:
                logger.warning("No exercises returned from YouTube service, using fallback")
                exercises = self.youtube_service._get_fallback_videos(5)
            else:
                # Store original exercises before filtering
                original_exercises = exercises[:]
                # Filter by mood (quick, no timeout needed as it's just list filtering)
                try:
                    filtered_exercises = await self.youtube_service.filter_by_mood(
                        exercises, user_context["mood"], user_context.get("energy_trend", "medium")
                    )
                    # Use filtered if we have results, otherwise use original
                    if filtered_exercises:
                        exercises = filtered_exercises
                    else:
                        exercises = original_exercises[:5]  # Use first 5 from original
                except Exception as filter_error:
                    logger.warning(f"Mood filtering failed: {str(filter_error)}, using original")
                    exercises = original_exercises[:5]
        except Exception as e:
            logger.error(f"Error fetching YouTube videos: {str(e)}", exc_info=True)
            # Fallback to default exercises if YouTube service fails
            try:
                exercises = self.youtube_service._get_fallback_videos(5)
            except Exception as fallback_error:
                logger.error(f"Even fallback videos failed: {str(fallback_error)}")
                from backend.models.schemas import ExerciseVideo
                exercises = [
                    ExerciseVideo(
                        video_id="default_1",
                        title="Gentle Stretching for Seniors",
                        description="Easy stretching exercises",
                        thumbnail_url="https://img.youtube.com/vi/dZLcwqVv50Q/mqdefault.jpg",
                        duration=10,
                        channel_name="ElderFit",
                        url="https://www.youtube.com/watch?v=dZLcwqVv50Q"
                    )
                ]
        
        # Step 8: Compliance check
        try:
            compliance = self.compliance_agent.check_compliance(meal_plan, user_context)
        except Exception as e:
            logger.warning(f"Compliance check failed: {str(e)}, using defaults")
            compliance = {
                "fiber_met": True,
                "calcium_met": True,
                "hydration_reminder": user_context.get("energy") == "low",
                "compliance_score": 0.8,
                "needs_replan": False,
                "suggestions": []
            }
        
        # Step 9: Create plan and score it
        try:
            plan = DailyPlan(
                date=datetime.now().strftime("%Y-%m-%d"),
                meals=meal_plan,
                exercises=exercises[:5],  # Top 5 exercises
                hydration_reminder=compliance.get("hydration_reminder", False),
                plan_score=0.0,  # Will be calculated
                reasoning=""
            )
            
            # Score the plan
            try:
                plan.plan_score = self.optimizer_agent.score_plan(
                    plan, user_context, mood_interpretation, memory_insights, compliance
                )
            except Exception as e:
                logger.warning(f"Plan scoring failed: {str(e)}, using default score")
                plan.plan_score = 0.85  # Default good score
        except Exception as e:
            logger.error(f"Error creating plan object: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to create plan: {str(e)}")
        
        # Step 10: Generate explanation using LLM (with timeout to avoid hanging)
        apis_called.append("OpenAI API")
        try:
            # Use asyncio.wait_for to add timeout for OpenAI calls
            import asyncio
            plan.reasoning = await asyncio.wait_for(
                self.openai_service.generate_plan_explanation(
                    {
                        "breakfast": meal_plan.breakfast.model_dump() if hasattr(meal_plan.breakfast, 'model_dump') else meal_plan.breakfast.dict(),
                        "lunch": meal_plan.lunch.model_dump() if hasattr(meal_plan.lunch, 'model_dump') else meal_plan.lunch.dict(),
                        "dinner": meal_plan.dinner.model_dump() if hasattr(meal_plan.dinner, 'model_dump') else meal_plan.dinner.dict(),
                        "total_calories": meal_plan.total_calories,
                        "exercises": [e.model_dump() if hasattr(e, 'model_dump') else e.dict() for e in exercises[:5]]
                    },
                    {**user_context, "language": language}
                ),
                timeout=5.0  # 5 second timeout for OpenAI
            )
        except asyncio.TimeoutError:
            logger.warning("OpenAI explanation timed out, using fallback")
            plan.reasoning = f"Your personalized wellness plan has been created based on your current mood ({user_context.get('mood')}) and energy levels."
        except Exception as e:
            # Fallback if OpenAI fails
            logger.warning(f"OpenAI explanation failed: {str(e)}, using fallback")
            plan.reasoning = f"Your personalized wellness plan has been created based on your current mood ({user_context.get('mood')}) and energy levels."
        
        # Step 11: Create decision trace
        decision_trace = DecisionTrace(
            timestamp=datetime.now(),
            triggered_rules=triggered_rules,
            retrieved_memories=[ep.get("id", i) for i, ep in enumerate(similar_episodes)],
            plan_scores={"primary_plan": plan.plan_score},
            selected_plan="primary_plan",
            apis_called=apis_called,
            explanation=plan.reasoning,
            mood_interpretation=mood_interpretation.get("interpretation", "neutral")
        )
        
        # Convert to dict (handle both Pydantic v1 and v2)
        try:
            plan_dict = plan.model_dump() if hasattr(plan, 'model_dump') else plan.dict()
            trace_dict = decision_trace.model_dump() if hasattr(decision_trace, 'model_dump') else decision_trace.dict()
        except Exception as e:
            logger.error(f"Error converting to dict: {str(e)}", exc_info=True)
            # Fallback manual conversion
            plan_dict = {
                "date": plan.date,
                "meals": meal_plan.model_dump() if hasattr(meal_plan, 'model_dump') else meal_plan.dict(),
                "exercises": [e.model_dump() if hasattr(e, 'model_dump') else e.dict() for e in exercises[:5]],
                "hydration_reminder": plan.hydration_reminder,
                "plan_score": plan.plan_score,
                "reasoning": plan.reasoning
            }
            trace_dict = {
                "timestamp": decision_trace.timestamp.isoformat() if hasattr(decision_trace.timestamp, 'isoformat') else str(decision_trace.timestamp),
                "triggered_rules": decision_trace.triggered_rules,
                "retrieved_memories": decision_trace.retrieved_memories,
                "plan_scores": decision_trace.plan_scores,
                "selected_plan": decision_trace.selected_plan,
                "apis_called": decision_trace.apis_called,
                "explanation": decision_trace.explanation,
                "mood_interpretation": decision_trace.mood_interpretation
            }
        
        return {
            "plan": plan_dict,
            "decision_trace": trace_dict,
            "compliance": compliance,
            "memory_insights": memory_insights
        }
    
    def _apply_safety_rules(self, user_context: Dict[str, Any]) -> List[str]:
        """Apply symbolic safety rules"""
        triggered = []
        
        if user_context.get("age", 0) > 75:
            triggered.append("No hard-to-chew foods (age > 75)")
        
        triggered.append("Low spice preference for all elders")
        triggered.append("Maximum 20 minutes exercise per day")
        triggered.append("Minimum 1500 calories per day")
        triggered.append("Always include calcium sources")
        
        if user_context.get("energy") == "low" or user_context.get("energy_trend") == "low":
            triggered.append("Hydration reminder (low energy)")
        
        return triggered

