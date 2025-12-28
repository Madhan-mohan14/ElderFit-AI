from typing import Dict, Any
from backend.models.schemas import DailyMealPlan
from backend.config import Config

class ComplianceMonitorAgent:
    """Monitors compliance with hydration, fiber, and calcium goals"""
    
    def check_compliance(self, plan: DailyMealPlan, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if plan meets compliance targets"""
        fiber_met = plan.total_fiber >= Config.TARGET_FIBER * 0.8  # 80% of target
        calcium_met = plan.total_calcium >= Config.TARGET_CALCIUM * 0.8
        
        # Check hydration reminder needed
        hydration_needed = (
            user_context.get("mood") in ["tired", "low"] or
            user_context.get("energy") == "low" or
            user_context.get("yesterday_adherence", 100) < 70
        )
        
        compliance_score = sum([fiber_met, calcium_met]) / 2.0
        
        return {
            "fiber_met": fiber_met,
            "calcium_met": calcium_met,
            "hydration_reminder": hydration_needed,
            "compliance_score": compliance_score,
            "needs_replan": compliance_score < 0.5,
            "suggestions": self._generate_suggestions(fiber_met, calcium_met, hydration_needed)
        }
    
    def _generate_suggestions(self, fiber_met: bool, calcium_met: bool, hydration_needed: bool) -> list:
        """Generate improvement suggestions"""
        suggestions = []
        if not fiber_met:
            suggestions.append("Consider adding more fruits, vegetables, or whole grains for fiber")
        if not calcium_met:
            suggestions.append("Consider adding dairy products, leafy greens, or fortified foods for calcium")
        if hydration_needed:
            suggestions.append("Remember to drink water throughout the day - aim for 8 glasses")
        return suggestions

