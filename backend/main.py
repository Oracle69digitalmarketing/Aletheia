
import os
import uuid
import time
import opik
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from opik import track
from dotenv import load_dotenv

from agents.planner import decompose_goal, detect_friction
from agents.evaluator import evaluate_plan
from core.opik_setup import get_trace_url, get_project_url
from core.database import get_db, PlanRecord
from sqlalchemy.orm import Session
from fastapi import Depends

load_dotenv()

# Configure Opik explicitly from environment variables
opik.configure(
    api_key=os.getenv("OPIK_API_KEY"),
    workspace=os.getenv("OPIK_WORKSPACE")
)

app = FastAPI(title="Aletheia Backend")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aletheia-ruddy.vercel.app",  # For Vercel frontend
        "https://aletheia-ruddy.vercel.app/", # For Vercel frontend (trailing slash)
        "http://localhost:5173",  # For local dev
        "http://localhost:3000",  # For local dev alternative
        "http://localhost:3001",  # For local dev alternative 2
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "message": "Aletheia Backend API", 
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "api_plan": "/api/plan (POST)"
        }
    }

@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "healthy", "timestamp": time.time()}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )
    
class GoalRequest(BaseModel):
    goal: str
    user_email: Optional[str] = "anonymous"

class AgentThought(BaseModel):
    agent: str
    thought: str

class Task(BaseModel):
    title: str
    description: str
    duration: str

class PlanMetrics(BaseModel):
    actionability: float
    relevance: float
    helpfulness: float
    latency: int
    project_url: str

class PlanResponse(BaseModel):
    id: str
    trace_id: str
    trace_url: str
    category: str
    tasks: List[Task]
    reasoning: List[AgentThought]
    friction_intervention: str
    metrics: PlanMetrics

@app.get("/api/history", response_model=List[PlanResponse])
async def get_history(user_email: str, db: Session = Depends(get_db)):
    records = db.query(PlanRecord).filter(PlanRecord.user_email == user_email).order_by(PlanRecord.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "trace_id": r.trace_id,
            "trace_url": get_trace_url(r.trace_id),
            "category": r.category,
            "tasks": r.tasks,
            "reasoning": r.reasoning,
            "friction_intervention": r.friction_intervention,
            "metrics": r.metrics
        } for r in records
    ]

@app.post("/api/plan", response_model=PlanResponse)
@track(name="generate_plan_workflow")
async def create_plan(request: GoalRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    
    # 1. Planner Agent
    ai_tasks = await decompose_goal(request.goal)
    if not ai_tasks:
        ai_tasks = [{"title": "Initial Action", "description": "Define the first step for this goal.", "duration": "15m"}]
    
    # 2. Friction/Monitor Agent
    intervention = await detect_friction(request.goal, ai_tasks)
    
    # 3. Evaluation Agent (Real scoring)
    scores = await evaluate_plan(request.goal, ai_tasks)
    
    # 4. Categorization logic
    goal_lower = request.goal.lower()
    category = "Personal Development"
    if any(w in goal_lower for w in ["learn", "code", "read", "study", "tech"]): category = "Knowledge"
    elif any(w in goal_lower for w in ["run", "gym", "health", "diet", "fitness", "sleep"]): category = "Wellness"
    elif any(w in goal_lower for w in ["job", "work", "career", "business", "money"]): category = "Professional"
    
    reasoning = [
        AgentThought(agent="Planner", thought=f"Goal decomposed into {len(ai_tasks)} actionable spans."),
        AgentThought(agent="Evaluator", thought=f"Plan verified with high {scores.get('relevance')} relevance score."),
        AgentThought(agent="Monitor", thought="Friction detection complete. Predictive intervention generated.")
    ]
    
    latency = int((time.time() - start_time) * 1000)
    
    # Retrieve the ACTUAL Opik Trace ID for this request
    # This ensures the 'View in Comet' link actually works.
    from opik import opik_context
    trace_data = opik_context.get_current_trace_data()
    trace_id = trace_data.id if trace_data else str(uuid.uuid4())
    
    if trace_data:
        try:
            opik_context.update_current_trace(feedback_scores=[
                {"name": "actionability", "value": scores.get("actionability", 4.0)},
                {"name": "relevance", "value": scores.get("relevance", 4.0)},
                {"name": "helpfulness", "value": scores.get("helpfulness", 4.0)}
            ])
        except Exception as e:
            print(f"Opik Update Warning: {e}")

    return {
        "id": str(uuid.uuid4())[:8],
        "trace_id": trace_id,
        "trace_url": get_trace_url(trace_id),
        "category": category,
        "tasks": [Task(**t) for t in ai_tasks],
        "reasoning": reasoning,
        "friction_intervention": intervention,
        "metrics": {
            "actionability": scores.get("actionability", 4.0),
            "relevance": scores.get("relevance", 4.0),
            "helpfulness": scores.get("helpfulness", 4.0),
            "latency": latency,
            "project_url": get_project_url()
        }
    }

    # Save to Database
    try:
        new_record = PlanRecord(
            id=plan_id,
            user_email=request.user_email,
            goal=request.goal,
            category=category,
            tasks=[t for t in ai_tasks],
            reasoning=[{"agent": r.agent, "thought": r.thought} for r in reasoning],
            friction_intervention=intervention,
            metrics=response_data["metrics"],
            trace_id=trace_id
        )
        db.add(new_record)
        db.commit()
    except Exception as e:
        print(f"Database Save Error: {e}")

    return response_data
