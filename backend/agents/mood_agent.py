from typing import Dict, Any

class MoodUnderstandingAgent:
    """Interprets user mood and maps to plan preferences"""
    
    def interpret_mood(self, mood: str, energy: str = "medium") -> Dict[str, Any]:
        """Interpret mood and generate plan preferences"""
        mood_preferences = {
            "happy": {
                "meal_complexity": "normal",
                "exercise_intensity": "normal",
                "meal_temperature": "normal",
                "encouragement_level": "high",
                "focus": ["variety", "engagement"]
            },
            "neutral": {
                "meal_complexity": "normal",
                "exercise_intensity": "normal",
                "meal_temperature": "normal",
                "encouragement_level": "medium",
                "focus": ["balance", "routine"]
            },
            "low": {
                "meal_complexity": "simple",
                "exercise_intensity": "gentle",
                "meal_temperature": "warm",
                "encouragement_level": "high",
                "focus": ["comfort", "nourishment"]
            },
            "stressed": {
                "meal_complexity": "simple",
                "exercise_intensity": "very_gentle",
                "meal_temperature": "warm",
                "encouragement_level": "high",
                "focus": ["calming", "breathing"]
            },
            "tired": {
                "meal_complexity": "simple",
                "exercise_intensity": "very_gentle",
                "meal_temperature": "warm",
                "encouragement_level": "medium",
                "focus": ["rest", "hydration"]
            }
        }
        
        preferences = mood_preferences.get(mood, mood_preferences["neutral"])
        
        # Adjust for low energy
        if energy == "low":
            preferences["exercise_intensity"] = "very_gentle"
            preferences["meal_complexity"] = "simple"
            preferences["focus"].append("rest")
        
        return {
            "interpretation": f"User is feeling {mood} with {energy} energy",
            "preferences": preferences,
            "suggested_meal_types": self._get_meal_suggestions(mood, energy),
            "suggested_exercise_types": self._get_exercise_suggestions(mood, energy)
        }
    
    def _get_meal_suggestions(self, mood: str, energy: str) -> list:
        """Get meal type suggestions based on mood"""
        suggestions = {
            "happy": ["varied", "colorful", "balanced"],
            "neutral": ["balanced", "routine"],
            "low": ["comfort", "warm", "soup"],
            "stressed": ["light", "easy", "soup"],
            "tired": ["simple", "warm", "liquid"]
        }
        return suggestions.get(mood, ["balanced"])
    
    def _get_exercise_suggestions(self, mood: str, energy: str) -> list:
        """Get exercise type suggestions"""
        suggestions = {
            "happy": ["stretching", "light movement"],
            "neutral": ["routine", "balance"],
            "low": ["chair yoga", "breathing"],
            "stressed": ["breathing", "meditation", "gentle stretching"],
            "tired": ["seated", "breathing", "restorative"]
        }
        return suggestions.get(mood, ["gentle movement"])

