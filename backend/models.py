from pydantic import BaseModel
from typing import List, Optional

class GoalRequest(BaseModel):
    goal: str
    user_email: Optional[str] = "anonymous"

class LogEntry(BaseModel):
    id: str
    timestamp: str
    level: str # 'INFO' | 'TRACE' | 'DEBUG' | 'WARN'
    source: str
    message: str

class AgentThought(BaseModel):
    agent: str
    thought: str
    timestamp: str = "" # Added timestamp

class Task(BaseModel):
    id: str = "" # Added id
    title: str
    description: str
    duration: str
    status: str = "todo" # Added status
    category: str = "Uncategorized" # Added category

class PlanMetrics(BaseModel):
    actionability: float
    relevance: float
    helpfulness: float
    latency: int
    projectUrl: str # Renamed to projectUrl

class PlanResponse(BaseModel):
    id: str
    originalGoal: str # Added originalGoal
    category: str
    tasks: List[Task]
    agentReasoning: List[AgentThought] # Renamed to agentReasoning
    traceId: str # Renamed to traceId
    traceUrl: str # Renamed to traceUrl
    logs: List[LogEntry] # Added logs
    frictionIntervention: str
    metrics: PlanMetrics
