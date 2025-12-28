from typing import List, Dict, Any
from backend.models.schemas import DailyPlan

class PlanOptimizerAgent:
    """Scores and selects the best plan from multiple options"""
    
    def score_plan(self, plan: DailyPlan, user_context: Dict[str, Any], 
                   preferences: Dict[str, Any], memory_insights: Dict[str, Any],
                   compliance: Dict[str, Any]) -> float:
        """Score a plan based on multiple factors"""
        scores = {
            "mood_fit": self._score_mood_fit(plan, preferences),
            "nutrient_completeness": self._score_nutrients(plan.meals, compliance),
            "preparation_simplicity": self._score_simplicity(plan.meals),
            "workout_duration": self._score_exercise_duration(plan.exercises, user_context),
            "engagement_history": self._score_engagement(plan, memory_insights),
            "calorie_adequacy": self._score_calories(plan.meals.total_calories, user_context.get("age", 70))
        }
        
        # Weighted average
        weights = {
            "mood_fit": 0.25,
            "nutrient_completeness": 0.25,
            "preparation_simplicity": 0.15,
            "workout_duration": 0.15,
            "engagement_history": 0.10,
            "calorie_adequacy": 0.10
        }
        
        total_score = sum(scores[key] * weights[key] for key in scores)
        return total_score
    
    def _score_mood_fit(self, plan: DailyPlan, preferences: Dict[str, Any]) -> float:
        """Score how well plan fits mood preferences"""
        pref_prefs = preferences.get("preferences", {})
        score = 0.5  # Base score
        
        # Check meal temperature
        if pref_prefs.get("meal_temperature") == "warm":
            warm_meals = sum(1 for meal in [plan.meals.breakfast, plan.meals.lunch, plan.meals.dinner]
                           if "warm" in meal.name.lower() or "soup" in meal.name.lower())
            score += (warm_meals / 3) * 0.3
        
        # Check simplicity
        if pref_prefs.get("meal_complexity") == "simple":
            avg_simplicity = sum((plan.meals.breakfast.simplicity_score or 0.7,
                                plan.meals.lunch.simplicity_score or 0.7,
                                plan.meals.dinner.simplicity_score or 0.7)) / 3
            score += avg_simplicity * 0.2
        
        return min(score, 1.0)
    
    def _score_nutrients(self, meals: Any, compliance: Dict[str, Any]) -> float:
        """Score nutrient completeness"""
        return compliance.get("compliance_score", 0.5)
    
    def _score_simplicity(self, meals: Any) -> float:
        """Score meal preparation simplicity"""
        simplicity_scores = [
            meals.breakfast.simplicity_score or 0.7,
            meals.lunch.simplicity_score or 0.7,
            meals.dinner.simplicity_score or 0.7
        ]
        return sum(simplicity_scores) / len(simplicity_scores)
    
    def _score_exercise_duration(self, exercises: list, user_context: Dict[str, Any]) -> float:
        """Score exercise duration appropriateness"""
        if not exercises:
            return 0.5
        
        total_duration = sum(ex.duration for ex in exercises)
        energy = user_context.get("energy", "medium")
        
        if energy == "low":
            ideal_duration = 10
        else:
            ideal_duration = 15
        
        # Score based on how close to ideal
        diff = abs(total_duration - ideal_duration)
        score = max(0, 1 - (diff / ideal_duration))
        return score
    
    def _score_engagement(self, plan: DailyPlan, memory_insights: Dict[str, Any]) -> float:
        """Score based on past engagement"""
        score = 0.5  # Base
        liked_foods = memory_insights.get("liked_foods", [])
        
        # Check if plan includes liked foods
        all_meal_names = " ".join([
            plan.meals.breakfast.name,
            plan.meals.lunch.name,
            plan.meals.dinner.name
        ]).lower()
        
        for liked_food in liked_foods[:3]:
            if liked_food.lower() in all_meal_names:
                score += 0.15
        
        return min(score, 1.0)
    
    def _score_calories(self, calories: float, age: int) -> float:
        """Score calorie adequacy"""
        from backend.config import Config
        target = Config.MIN_CALORIES + (Config.MAX_CALORIES - Config.MIN_CALORIES) * (90 - age) / 45
        
        if calories < target * 0.9:
            return 0.6
        elif calories > target * 1.2:
            return 0.7
        else:
            return 1.0

