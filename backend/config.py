import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    USDA_API_KEY = os.getenv("USDA_API_KEY", "")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    GOOGLE_CALENDAR_API_KEY = os.getenv("GOOGLE_CALENDAR_API_KEY", "")
    
    # Application Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./elderfit_ai.db")
    
    # Logging
    LOG_DIR = os.getenv("LOG_DIR", "./logs")
    
    # Elder Safety Constraints
    ELDER_AGE_RANGE = (45, 90)
    MIN_CALORIES = 1500
    MAX_CALORIES = 2200
    TARGET_FIBER = 25  # grams
    TARGET_CALCIUM = 1200  # mg
    TARGET_WATER = 2000  # ml
    
    # Exercise Constraints
    MIN_EXERCISE_DURATION = 5  # minutes
    MAX_EXERCISE_DURATION = 20  # minutes

