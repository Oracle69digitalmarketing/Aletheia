
import { Plan, TaskStatus, LogEntry } from "../types";

const API_URL = "http://localhost:8000";

export const generateAgenticPlan = async (goal: string): Promise<Plan> => {
  const response = await fetch(`${API_URL}/api/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal })
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown Error' }));
    throw new Error(errorData.detail || 'Failed to reach Aletheia Backend');
  }

  const data = await response.json();

  const logs: LogEntry[] = [
    { id: '1', timestamp: new Date().toLocaleTimeString(), level: 'INFO', source: 'SYSTEM', message: `POST /api/plan 200 OK` },
    { id: '2', timestamp: new Date().toLocaleTimeString(), level: 'TRACE', source: 'OPIK', message: `Trace ID [${data.trace_id}] synchronized.` },
    { id: '3', timestamp: new Date().toLocaleTimeString(), level: 'DEBUG', source: 'EVALUATOR', message: `Scoring complete: Rel ${data.metrics.relevance}` },
  ];

  return {
    id: data.id,
    originalGoal: goal,
    category: data.category,
    tasks: data.tasks.map((t: any) => ({
      ...t,
      id: Math.random().toString(36).substr(2, 9),
      status: TaskStatus.TODO,
      category: data.category
    })),
    agentReasoning: data.reasoning.map((r: any) => ({
      ...r,
      timestamp: new Date().toLocaleTimeString()
    })),
    traceId: data.trace_id,
    traceUrl: data.trace_url,
    logs: logs,
    frictionIntervention: data.friction_intervention,
    metrics: {
      actionability: data.metrics.actionability,
      relevance: data.metrics.relevance,
      helpfulness: data.metrics.helpfulness,
      latency: data.metrics.latency,
      projectUrl: data.metrics.project_url
    }
  };
};
