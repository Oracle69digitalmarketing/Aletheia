
import os
import sys

# Add the parent directory of 'backend' to sys.path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid
import time
import opik
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from opik import track
from dotenv import load_dotenv
from datetime import datetime # Added datetime import
from typing import List

from agents.planner import decompose_goal, detect_friction
from agents.evaluator import evaluate_plan
from core.opik_setup import get_trace_url, get_project_url, get_project
from core.database import get_db, PlanRecord
from sqlalchemy.orm import Session
from fastapi import Depends

load_dotenv()

# Configure Opik explicitly from environment variables with fallbacks
def configure_opik():
    api_key = os.getenv("OPIK_API_KEY")
    workspace = os.getenv("OPIK_WORKSPACE")

    # Ignore placeholder keys
    if api_key and ("your_" in api_key or "api_key" in api_key.lower()):
        api_key = None
    if workspace and ("your_" in workspace or "workspace" in workspace.lower()):
        workspace = None

    if not api_key:
        print("Opik API Key missing or placeholder. Tracing disabled.")
        return

    try:
        opik.configure(api_key=api_key, workspace=workspace)
    except Exception as e:
        print(f"Opik Configuration Warning: {e}. Tracing might be limited.")

configure_opik()

app = FastAPI(title="Aletheia Backend")

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://aletheia-gfzrzo11w-oracle69.vercel.app",
    "https://aletheia-ruddy.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aletheia-gfzrzo11w-oracle69.vercel.app",
        "https://aletheia-ruddy.vercel.app",
        "https://aletheia-ruddy-vercel-app.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000"
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
    google_api_key = os.getenv("GOOGLE_API_KEY")
    opik_api_key = os.getenv("OPIK_API_KEY")

    return {
        "status": "healthy",
        "timestamp": time.time(),
        "diagnostics": {
            "google_api_key_set": bool(google_api_key and "your_" not in google_api_key.lower()),
            "opik_api_key_set": bool(opik_api_key and "your_" not in opik_api_key.lower()),
            "opik_workspace": os.getenv("OPIK_WORKSPACE")
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("Origin", "*")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )
    
from backend.models import GoalRequest, LogEntry, AgentThought, Task, PlanMetrics, PlanResponse

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
@track(name="generate_plan_workflow", project_name=get_project())
async def create_plan(request: GoalRequest, db: Session = Depends(get_db)):
    start_time = time.time()

    # 1. Planner Agent
    try:
        ai_tasks, planner_thought = await decompose_goal(request.goal)
    except Exception as e:
        # If the LLM fails, we raise an error instead of returning mock data
        # this helps the user diagnose the issue (e.g. invalid API key)
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Aletheia Planner Agent Error: {str(e)}")

    if not ai_tasks:
        ai_tasks = [{"title": "Initial Action", "description": "Define the first step for this goal.", "duration": "15m"}]
        planner_thought = "Standardized fallback task generated due to empty model response."

    # 2. Friction/Monitor Agent
    intervention, monitor_thought = await detect_friction(request.goal, ai_tasks)
    
    # 3. Evaluation Agent (Real scoring)
    try:
        scores = await evaluate_plan(request.goal, ai_tasks)
    except Exception as e:
        print(f"Evaluator Agent Error (caught in main.py): {e}")
        scores = {
            "actionability": 0.0,
            "relevance": 0.0,
            "helpfulness": 0.0,
            "reasoning": f"Evaluation failed due to: {str(e)[:50]}..."
        }
    
    # 4. Categorization logic
    goal_lower = request.goal.lower()
    category = "Personal Development"
    if any(w in goal_lower for w in ["learn", "code", "read", "study", "tech"]): category = "Knowledge"
    elif any(w in goal_lower for w in ["run", "gym", "health", "diet", "fitness", "sleep"]): category = "Wellness"
    elif any(w in goal_lower for w in ["job", "work", "career", "business", "money"]): category = "Professional"

    reasoning = [
        AgentThought(agent="Planner", thought=planner_thought, timestamp=datetime.now().isoformat()),
        AgentThought(agent="Evaluator", thought=scores.get("reasoning", "Plan verified for actionability and relevance."), timestamp=datetime.now().isoformat()),
        AgentThought(agent="Monitor", thought=monitor_thought, timestamp=datetime.now().isoformat())
    ]

    latency = int((time.time() - start_time) * 1000)

    # Retrieve the ACTUAL Opik Trace ID for this request
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

    # Print results as requested
    print("\n" + "="*50)
    print(f"PLAN GENERATED FOR: {request.goal}")
    print(f"Category: {category}")
    print(f"Tasks ({len(ai_tasks)}):")
    for t in ai_tasks:
        print(f"  - {t.get('title')} ({t.get('duration')})")
    print(f"Friction Intervention: {intervention}")
    print(f"Scores: {scores}")
    print(f"Trace URL: {get_trace_url(trace_id)}")
    print("="*50 + "\n")

    plan_id = str(uuid.uuid4())[:8]

    # Prepare tasks with new fields
    formatted_tasks = []
    for task_dict in ai_tasks:
        formatted_tasks.append(Task(
            id=str(uuid.uuid4()),
            title=task_dict.get('title', 'Untitled Task'),
            description=task_dict.get('description', ''),
            duration=task_dict.get('duration', '0m'),
            status="todo",
            category="Uncategorized"
        ))

    response_data = {
        "id": plan_id,
        "originalGoal": request.goal,
        "category": category,
        "tasks": formatted_tasks,
        "agentReasoning": reasoning, # Renamed
        "traceId": trace_id, # Renamed
        "traceUrl": get_trace_url(trace_id), # Renamed
        "logs": [], # Added logs
        "frictionIntervention": intervention,
        "metrics": {
            "actionability": scores.get("actionability", 4.0),
            "relevance": scores.get("relevance", 4.0),
            "helpfulness": scores.get("helpfulness", 4.0),
            "latency": latency,
            "projectUrl": get_project_url() # Renamed
        }
    }

    # Save to Database
    try:
        new_record = PlanRecord(
            id=plan_id,
            user_email=request.user_email,
            goal=request.goal,
            category=category,
            tasks=[t.model_dump() for t in formatted_tasks], # Store as dictionaries
            reasoning=[r.model_dump() for r in reasoning], # Store as dictionaries
            friction_intervention=intervention,
            metrics=response_data["metrics"],
            trace_id=trace_id
        )
        db.add(new_record)
        db.commit()
    except Exception as e:
        print(f"Database Save Error: {e}")

    return response_data
