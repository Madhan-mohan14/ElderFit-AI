from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import Config
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    allergies = Column(JSON, default=list)
    diet_type = Column(String, default="balanced")
    medical_conditions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class WellnessEpisode(Base):
    __tablename__ = "wellness_episodes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    date = Column(String)
    mood = Column(String)
    appetite = Column(String)
    energy = Column(String)
    nutrients_met = Column(JSON)
    adherence = Column(Float)
    liked_foods = Column(JSON, default=list)
    liked_videos = Column(JSON, default=list)
    plan_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class DailyPlan(Base):
    __tablename__ = "daily_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    date = Column(String)
    plan_data = Column(JSON)
    decision_trace = Column(JSON)
    compliance = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class DecisionLog(Base):
    __tablename__ = "decision_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    trace_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

