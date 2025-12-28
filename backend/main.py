from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from typing import List
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path to allow imports when running from backend directory
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.config import Config
from backend.models import schemas, database
from backend.agents.reasoner_agent import ReasonerAgent
from backend.services.openai_service import OpenAIService
from backend.agents.memory_agent import MemoryAgent
from backend.middleware import LoggingMiddleware, SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("ENVIRONMENT") != "production" else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Config.LOG_DIR, "app.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ElderFit AI API",
    description="Wellness assistant for elderly users",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Get allowed origins from environment or use defaults
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Initialize database
try:
    database.init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    raise

# Initialize agents with error handling
try:
    reasoner = ReasonerAgent()
    openai_service = OpenAIService()
    memory_agent = MemoryAgent()
    logger.info("Agents initialized successfully")
except Exception as e:
    logger.error(f"Agent initialization failed: {str(e)}")
    raise

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    # Create logs directory
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    logger.info("ElderFit AI API starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"API running on {Config.API_HOST}:{Config.API_PORT}")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("ElderFit AI API shutting down...")

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = exc.errors()
    logger.warning(f"Validation error: {errors}")
    
    # Create user-friendly error messages
    error_messages = []
    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "Invalid value")
        error_messages.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "detail": "; ".join(error_messages),
            "details": errors,
            "message": f"Please check your input: {'; '.join(error_messages)}"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

@app.get("/")
async def root():
    return {"message": "ElderFit AI API", "status": "running"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Check database connection
        db = next(database.get_db())
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "disconnected"
    
    # Check API keys
    api_keys_status = {
        "openai": "configured" if Config.OPENAI_API_KEY else "missing",
        "usda": "configured" if Config.USDA_API_KEY else "missing",
        "youtube": "configured" if Config.YOUTUBE_API_KEY else "missing"
    }
    
    overall_status = "healthy" if db_status == "connected" else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "api_keys": api_keys_status,
        "version": "1.0.0"
    }

@app.post("/api/users", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(profile: schemas.UserProfile, db: Session = Depends(database.get_db)):
    """Create or update user profile"""
    try:
        # Validate age range
        if not (Config.ELDER_AGE_RANGE[0] <= profile.age <= Config.ELDER_AGE_RANGE[1]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Age must be between {Config.ELDER_AGE_RANGE[0]} and {Config.ELDER_AGE_RANGE[1]}"
            )
        
        user = database.User(
            age=profile.age,
            allergies=profile.allergies or [],
            diet_type=profile.diet_type,
            medical_conditions=profile.medical_conditions or []
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User created: ID={user.id}, Age={user.age}")
        return {
            "user_id": user.id,
            "message": "User created successfully",
            "age": user.age,
            "diet_type": user.diet_type
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )

@app.post("/api/check-in/generate-plan")
async def generate_plan(
    request_data: schemas.GeneratePlanRequest,
    language: str = "en",
    db: Session = Depends(database.get_db)
):
    """Generate daily wellness plan"""
    try:
        # Log received data for debugging
        logger.info(f"Received plan generation request: age={request_data.age}, mood={request_data.mood}, appetite={request_data.appetite}, energy={request_data.energy_level}")
        
        # Extract user profile and check-in data from validated request
        user_profile_data = {
            "age": request_data.age,
            "allergies": request_data.allergies or [],
            "diet_type": request_data.diet_type,
            "medical_conditions": request_data.medical_conditions or []
        }
        
        # Validate age range (additional validation, though schema already validates)
        if not (Config.ELDER_AGE_RANGE[0] <= user_profile_data["age"] <= Config.ELDER_AGE_RANGE[1]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Age must be between {Config.ELDER_AGE_RANGE[0]} and {Config.ELDER_AGE_RANGE[1]}"
            )
        
        check_in_data = {
            "mood": request_data.mood.value if hasattr(request_data.mood, 'value') else str(request_data.mood),
            "appetite": request_data.appetite.value if hasattr(request_data.appetite, 'value') else str(request_data.appetite),
            "yesterday_adherence": float(request_data.yesterday_adherence),
            "energy_level": request_data.energy_level.value if hasattr(request_data.energy_level, 'value') else str(request_data.energy_level)
        }
        
        # Create user if doesn't exist (simplified - in production use auth)
        user = db.query(database.User).filter_by(age=user_profile_data["age"]).first()
        if not user:
            user = database.User(
                age=user_profile_data["age"],
                allergies=user_profile_data["allergies"],
                diet_type=user_profile_data["diet_type"],
                medical_conditions=user_profile_data["medical_conditions"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Generate plan using reasoner
        try:
            logger.info("Starting plan generation with reasoner...")
            result = await reasoner.generate_plan(
                user_profile_data,
                check_in_data,
                language
            )
            logger.info(f"Plan generation successful. Plan has {len(result.get('plan', {}).get('exercises', []))} exercises")
        except ValueError as e:
            # Validation errors
            logger.warning(f"Validation error in plan generation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data: {str(e)}"
            )
        except Exception as e:
            # Log full error for debugging
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Error in reasoner.generate_plan: {str(e)}\n{error_trace}")
            db.rollback()
            # Return a more user-friendly error message
            error_msg = str(e)
            if "enum" in error_msg.lower() or "invalid" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid input: {error_msg}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate plan. Please check backend logs for details."
                )
        
        # Store plan in database
        try:
            plan_record = database.DailyPlan(
                user_id=user.id,
                date=result["plan"].get("date", datetime.now().strftime("%Y-%m-%d")),
                plan_data=result["plan"],
                decision_trace=result["decision_trace"],
                compliance=result["compliance"]
            )
            db.add(plan_record)
            
            # Store decision log
            log_record = database.DecisionLog(
                user_id=user.id,
                trace_data=result["decision_trace"]
            )
            db.add(log_record)
            db.commit()
            db.refresh(plan_record)
        except Exception as e:
            logger.error(f"Error storing plan in database: {str(e)}", exc_info=True)
            db.rollback()
            # Still return the plan even if database storage fails
            return {
                "plan": result["plan"],
                "decision_trace": result["decision_trace"],
                "compliance": result["compliance"],
                "memory_insights": result["memory_insights"],
                "user_id": user.id,
                "plan_id": None,
                "warning": "Plan generated but not saved to database"
            }
        
        response_data = {
            "plan": result["plan"],
            "decision_trace": result["decision_trace"],
            "compliance": result["compliance"],
            "memory_insights": result.get("memory_insights", {}),
            "user_id": user.id,
            "plan_id": plan_record.id
        }
        
        logger.info(f"Returning plan response. Plan structure: has_plan={bool(response_data.get('plan'))}, has_exercises={bool(response_data.get('plan', {}).get('exercises'))}, exercise_count={len(response_data.get('plan', {}).get('exercises', []))}")
        
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error generating plan: {str(e)}\n{error_trace}")
        db.rollback()
        
        # Provide more helpful error messages
        error_msg = str(e)
        if "AttributeError" in error_msg or "'NoneType' object" in error_msg:
            detail = "An internal error occurred. Please check that all services are properly configured."
        elif "Connection" in error_msg or "timeout" in error_msg.lower():
            detail = "Unable to connect to external services. Please check your internet connection and API keys."
        elif "validation" in error_msg.lower() or "ValidationError" in error_msg:
            detail = "Invalid input data. Please check all fields are filled correctly."
        else:
            detail = f"Error generating plan: {error_msg[:200]}"  # Limit error message length
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

@app.post("/api/feedback")
async def submit_feedback(
    feedback: schemas.FeedbackRequest,
    db: Session = Depends(database.get_db)
):
    """Submit end-of-day feedback"""
    try:
        # Get user (simplified - in production use auth)
        user = db.query(database.User).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please create a profile first."
            )
        
        # Store feedback as wellness episode
        episode_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "mood": "neutral",  # Would come from previous check-in
            "appetite": "normal",
            "energy": "medium",
            "nutrients_met": {"fiber": True, "calcium": True},
            "adherence": float(feedback.diet_followed),
            "liked_foods": feedback.liked_foods or [],
            "liked_videos": feedback.liked_videos or [],
            "plan_score": 0.8
        }
        
        # Store in memory agent
        try:
            memory_agent.store_episode(episode_data)
        except Exception as e:
            logger.warning(f"Failed to store episode in memory agent: {str(e)}")
        
        # Store in database
        episode = database.WellnessEpisode(
            user_id=user.id,
            **episode_data
        )
        db.add(episode)
        db.commit()
        db.refresh(episode)
        
        logger.info(f"Feedback submitted successfully for user {user.id}, episode {episode.id}")
        return {"message": "Feedback submitted successfully", "episode_id": episode.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting feedback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )

@app.post("/api/chat", response_model=schemas.ChatResponse)
async def chat(message: schemas.ChatMessage, db: Session = Depends(database.get_db)):
    """Chat with ElderFit AI"""
    try:
        # Validate message
        if not message.message or len(message.message.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        if len(message.message) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message too long (max 1000 characters)"
            )
        
        # Get user context (simplified - in production use auth)
        user = db.query(database.User).first()
        user_context = {
            "age": user.age if user else 70,
            "mood": "neutral"
        }
        
        # Always try to get a response (OpenAI service handles fallback internally)
        logger.info(f"Processing chat message: '{message.message[:50]}...' (language: {message.language})")
        
        try:
            response_text = await openai_service.chat_response(
                message.message,
                user_context,
                message.language
            )
            logger.info(f"Chat response generated successfully (length: {len(response_text)})")
        except Exception as e:
            logger.error(f"Error in chat_response: {str(e)}", exc_info=True)
            # Use intelligent fallback from the service
            response_text = openai_service._get_intelligent_fallback(
                message.message,
                user_context,
                message.language
            )
        
        return schemas.ChatResponse(
            response=response_text,
            language=message.language
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate chat response"
        )

@app.get("/api/decision-traces/{plan_id}")
async def get_decision_trace(plan_id: int, db: Session = Depends(database.get_db)):
    """Get decision trace for a plan"""
    plan = db.query(database.DailyPlan).filter_by(id=plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return {
        "plan_id": plan.id,
        "date": plan.date,
        "decision_trace": plan.decision_trace,
        "compliance": plan.compliance
    }

@app.get("/api/memory-insights")
async def get_memory_insights(
    user_id: int = None,
    db: Session = Depends(database.get_db)
):
    """Get memory insights"""
    try:
        insights = memory_agent.get_preferences()
        similar_episodes = memory_agent.retrieve_similar(
            {"mood": "neutral", "appetite": "normal", "energy": "medium"},
            top_k=5
        )
        
        return {
            "preferences": insights or {},
            "similar_episodes": similar_episodes[:3] if similar_episodes else [],  # Top 3
            "total_episodes": len(similar_episodes) if similar_episodes else 0
        }
    except Exception as e:
        logger.error(f"Error fetching memory insights: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch memory insights"
        )

@app.get("/api/history")
async def get_user_history(
    limit: int = 30,
    user_id: int = None,
    db: Session = Depends(database.get_db)
):
    """Get user's wellness history"""
    try:
        query = db.query(database.WellnessEpisode)
        
        # Filter by user_id if provided
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        episodes = query.order_by(
            database.WellnessEpisode.date.desc()
        ).limit(min(limit, 100)).all()  # Max 100 episodes
        
        return {
            "episodes": [
                {
                    "id": ep.id,
                    "date": ep.date,
                    "mood": ep.mood,
                    "adherence": ep.adherence,
                    "liked_foods": ep.liked_foods or [],
                    "liked_videos": ep.liked_videos or []
                }
                for ep in episodes
            ],
            "total": len(episodes)
        }
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch history"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)

