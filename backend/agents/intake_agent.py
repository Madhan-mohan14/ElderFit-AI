from typing import Dict, Any
from backend.models.schemas import UserProfile, CheckInRequest

class IntakeAgent:
    """Collects user information and daily check-in data"""
    
    def process_intake(self, profile: UserProfile, check_in: CheckInRequest) -> Dict[str, Any]:
        """Process user intake information"""
        return {
            "age": profile.age,
            "allergies": profile.allergies,
            "diet_type": profile.diet_type,
            "medical_conditions": profile.medical_conditions,
            "mood": check_in.mood.value,
            "appetite": check_in.appetite.value,
            "energy": check_in.energy_level.value if check_in.energy_level else "medium",
            "yesterday_adherence": check_in.yesterday_adherence,
            "needs_attention": check_in.yesterday_adherence < 50 or check_in.mood.value in ["low", "stressed"]
        }

