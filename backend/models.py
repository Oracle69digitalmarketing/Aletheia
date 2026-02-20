from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Existing Aletheia models
class GoalRequest(BaseModel):
    goal: str
    user_email: Optional[str] = "anonymous"

class LogEntry(BaseModel):
    id: str
    timestamp: str
    level: str
    source: str
    message: str

class AgentThought(BaseModel):
    agent: str
    thought: str
    timestamp: str = ""

class Task(BaseModel):
    id: str = ""
    title: str
    description: str
    duration: str
    status: str = "todo"
    category: str = "Uncategorized"

class PlanMetrics(BaseModel):
    actionability: float
    relevance: float
    helpfulness: float
    latency: int
    projectUrl: str

class PlanResponse(BaseModel):
    id: str
    originalGoal: str
    category: str
    tasks: List[Task]
    agentReasoning: List[AgentThought]
    traceId: str
    traceUrl: str
    logs: List[LogEntry]
    frictionIntervention: str
    metrics: PlanMetrics

# New Ondo Connect models
class UserBase(BaseModel):
    phone: str
    name: Optional[str] = None
    language: str = "en"
    role: Optional[str] = None

class FarmerRegisterRequest(UserBase):
    lga: str
    crops: List[Dict[str, Any]]
    subscriptions: List[str] = []

class AdviceResponse(BaseModel):
    farmerId: str
    advice: str
    weatherAlert: Optional[str] = None
    marketPrices: Optional[Dict[str, Any]] = None

class ListingCreateRequest(BaseModel):
    sellerId: str
    type: str  # 'product'|'service'|'waste'
    category: str
    title: str
    description: str
    price: float
    unit: str
    images: List[str] = []

class WasteCollectionRequest(BaseModel):
    requesterName: str
    requesterPhone: str
    address: str
    wasteType: str
    estimatedKg: float
