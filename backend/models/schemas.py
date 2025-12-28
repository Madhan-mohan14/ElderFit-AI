from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Mood(str, Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    LOW = "low"
    STRESSED = "stressed"
    TIRED = "tired"

class AppetiteLevel(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class EnergyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class UserProfile(BaseModel):
    age: int = Field(..., ge=45, le=90)
    allergies: List[str] = Field(default_factory=list)
    diet_type: str = Field(default="balanced")  # vegetarian, vegan, balanced, etc.
    medical_conditions: List[str] = Field(default_factory=list)

class CheckInRequest(BaseModel):
    mood: Mood
    appetite: AppetiteLevel
    yesterday_adherence: float = Field(..., ge=0, le=100)
    energy_level: Optional[EnergyLevel] = None

class MealItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: Optional[float] = None
    calcium: Optional[float] = None
    vitamin_d: Optional[float] = None
    omega_3: Optional[float] = None
    preparation_time: Optional[int] = None  # minutes
    simplicity_score: Optional[float] = None  # 0-1

class DailyMealPlan(BaseModel):
    breakfast: MealItem
    lunch: MealItem
    dinner: MealItem
    snacks: List[MealItem] = []
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    total_calcium: float

class ExerciseVideo(BaseModel):
    video_id: str
    title: str
    description: str
    thumbnail_url: str
    duration: int  # minutes
    channel_name: str
    url: str

class DailyPlan(BaseModel):
    date: str
    meals: DailyMealPlan
    exercises: List[ExerciseVideo]
    hydration_reminder: bool
    plan_score: float
    reasoning: str

class DecisionTrace(BaseModel):
    timestamp: datetime
    triggered_rules: List[str]
    retrieved_memories: List[Dict[str, Any]]
    plan_scores: Dict[str, float]
    selected_plan: str
    apis_called: List[str]
    explanation: str
    mood_interpretation: str

class FeedbackRequest(BaseModel):
    plan_id: str
    diet_followed: float = Field(..., ge=0, le=100)
    exercise_completed: bool
    liked_foods: List[str] = []
    disliked_foods: List[str] = []
    liked_videos: List[str] = []
    disliked_videos: List[str] = []

class WellnessEpisode(BaseModel):
    date: str
    mood: Mood
    appetite: AppetiteLevel
    energy: EnergyLevel
    nutrients_met: Dict[str, bool]
    adherence: float
    liked_foods: List[str]
    liked_videos: List[str]
    plan_score: float

class ChatMessage(BaseModel):
    message: str
    language: str = "en"  # en, hi, te

class ChatResponse(BaseModel):
    response: str
    language: str

class GeneratePlanRequest(BaseModel):
    """Combined request model for plan generation"""
    # User profile fields
    age: int = Field(..., ge=45, le=90, description="User age (required)")
    allergies: List[str] = Field(default_factory=list)
    diet_type: str = Field(default="balanced")
    medical_conditions: List[str] = Field(default_factory=list)
    
    # Check-in fields
    mood: Mood
    appetite: AppetiteLevel = AppetiteLevel.NORMAL
    yesterday_adherence: float = Field(default=80, ge=0, le=100)
    energy_level: EnergyLevel = EnergyLevel.MEDIUM

