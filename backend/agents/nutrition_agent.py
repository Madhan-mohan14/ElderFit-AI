from typing import Dict, Any, List
from backend.services.nutrition_service import NutritionService
from backend.models.schemas import DailyMealPlan, MealItem
from backend.config import Config

class NutritionPlannerAgent:
    """Generates constraint-aware elder diet plans"""
    
    def __init__(self):
        self.nutrition_service = NutritionService()
    
    async def generate_plan(self, user_context: Dict[str, Any], preferences: Dict[str, Any]) -> DailyMealPlan:
        """Generate daily meal plan"""
        # Get meals for each meal type
        breakfast = await self.nutrition_service.get_elder_friendly_meal(
            "breakfast", preferences
        )
        lunch = await self.nutrition_service.get_elder_friendly_meal(
            "lunch", preferences
        )
        dinner = await self.nutrition_service.get_elder_friendly_meal(
            "dinner", preferences
        )
        
        # Adjust meals based on preferences
        breakfast = self._adjust_for_preferences(breakfast, preferences, "breakfast")
        lunch = self._adjust_for_preferences(lunch, preferences, "lunch")
        dinner = self._adjust_for_preferences(dinner, preferences, "dinner")
        
        # Add snacks if needed
        snacks = []
        total_calories = breakfast.calories + lunch.calories + dinner.calories
        if total_calories < Config.MIN_CALORIES:
            snack = await self.nutrition_service.get_elder_friendly_meal(
                "snack", preferences
            )
            snacks.append(snack)
            total_calories += snack.calories
        
        # Ensure calorie targets
        breakfast, lunch, dinner = self._adjust_calories(
            breakfast, lunch, dinner, user_context.get("age", 70)
        )
        
        # Calculate totals
        total_protein = breakfast.protein + lunch.protein + dinner.protein + sum(s.protein for s in snacks)
        total_carbs = breakfast.carbs + lunch.carbs + dinner.carbs + sum(s.carbs for s in snacks)
        total_fat = breakfast.fat + lunch.fat + dinner.fat + sum(s.fat for s in snacks)
        total_fiber = (breakfast.fiber or 0) + (lunch.fiber or 0) + (dinner.fiber or 0) + sum(s.fiber or 0 for s in snacks)
        total_calcium = (breakfast.calcium or 0) + (lunch.calcium or 0) + (dinner.calcium or 0) + sum(s.calcium or 0 for s in snacks)
        
        return DailyMealPlan(
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            snacks=snacks,
            total_calories=total_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat,
            total_fiber=total_fiber,
            total_calcium=total_calcium
        )
    
    def _adjust_for_preferences(self, meal: MealItem, preferences: Dict[str, Any], meal_type: str) -> MealItem:
        """Adjust meal based on mood and preferences"""
        mood_prefs = preferences.get("preferences", {})
        
        # Adjust name based on temperature preference
        if mood_prefs.get("meal_temperature") == "warm" and "soup" not in meal.name.lower():
            meal.name = f"Warm {meal.name}"
        
        # Adjust simplicity
        if mood_prefs.get("meal_complexity") == "simple":
            meal.simplicity_score = min(meal.simplicity_score or 0.7, 0.9)
            meal.preparation_time = max(5, (meal.preparation_time or 15) - 5)
        
        return meal
    
    def _adjust_calories(self, breakfast: MealItem, lunch: MealItem, dinner: MealItem, age: int) -> tuple:
        """Adjust meal calories to meet elder requirements"""
        target_calories = Config.MIN_CALORIES + (Config.MAX_CALORIES - Config.MIN_CALORIES) * (90 - age) / 45
        current_total = breakfast.calories + lunch.calories + dinner.calories
        
        if current_total < target_calories:
            ratio = target_calories / current_total
            breakfast.calories *= ratio
            lunch.calories *= ratio
            dinner.calories *= ratio
        
        return breakfast, lunch, dinner

