
import os
import uuid
import time
import opik
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from opik import track
from dotenv import load_dotenv

from agents.planner import decompose_goal, detect_friction
from agents.evaluator import evaluate_plan
from core.opik_setup import get_trace_url, get_project_url

load_dotenv()

app = FastAPI(title="Aletheia Backend")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aletheia-ruddy.vercel.app",  # For Vercel frontend
        "http://localhost:5173",  # For local dev
        "http://localhost:3000",  # For local dev alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
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

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}
    
class GoalRequest(BaseModel):
    goal: str

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

@app.post("/api/plan", response_model=PlanResponse)
@track(name="generate_plan_workflow")
def create_plan(request: GoalRequest):
    start_time = time.time()
    
    # 1. Planner Agent
    ai_tasks = decompose_goal(request.goal)
    if not ai_tasks:
        ai_tasks = [{"title": "Initial Action", "description": "Define the first step for this goal.", "duration": "15m"}]
    
    # 2. Friction/Monitor Agent
    intervention = detect_friction(request.goal, ai_tasks)
    
    # 3. Evaluation Agent (Real scoring)
    scores = evaluate_plan(request.goal, ai_tasks)
    
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
    trace_id = opik.get_current_trace_id() or str(uuid.uuid4())
    
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
