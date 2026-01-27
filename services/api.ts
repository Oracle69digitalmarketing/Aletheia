
import { Plan, TaskStatus, LogEntry } from "../types";

/**
 * PRODUCTION SETUP:
 * Replace the string below with your actual Render backend URL 
 * (e.g., https://aletheia-backend.onrender.com)
 */
const PRODUCTION_API_URL = "https://aletheia-backend-yu1n.onrender.com"; 

const API_URL = import.meta.env.VITE_API_URL || "https://aletheia-backend-yu1n.onrender.com";

export const generateAgenticPlan = async (goal: string): Promise<Plan> => {
  // Add a trailing slash check or ensure consistency
  const endpoint = `${API_URL.replace(/\/$/, '')}/api/plan`;
  
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Service Unreachable' }));
      throw new Error(errorData.detail || `Server responded with ${response.status}`);
    }

    const data = await response.json();

    if (!data || !data.tasks || !data.metrics) {
      throw new Error("Invalid response format from Aletheia Engine.");
    }

    const logs: LogEntry[] = [
      { id: '1', timestamp: new Date().toLocaleTimeString(), level: 'INFO', source: 'SYSTEM', message: `POST /api/plan 200 OK` },
      { id: '2', timestamp: new Date().toLocaleTimeString(), level: 'TRACE', source: 'OPIK', message: `Trace ID [${data.trace_id || 'N/A'}] synchronized.` },
      { id: '3', timestamp: new Date().toLocaleTimeString(), level: 'DEBUG', source: 'EVALUATOR', message: `Scoring complete: Rel ${data.metrics.relevance || 'N/A'}` },
    ];

    return {
      id: data.id || Math.random().toString(36).substr(2, 8),
      originalGoal: goal,
      category: data.category || "General",
      tasks: (data.tasks || []).map((t: any) => ({
        ...t,
        id: Math.random().toString(36).substr(2, 9),
        status: TaskStatus.TODO,
        category: data.category || "General"
      })),
      agentReasoning: (data.reasoning || []).map((r: any) => ({
        ...r,
        timestamp: new Date().toLocaleTimeString()
      })),
      traceId: data.trace_id || "",
      traceUrl: data.trace_url || "",
      logs: logs,
      frictionIntervention: data.friction_intervention || "No friction detected.",
      metrics: {
        actionability: data.metrics.actionability || 0,
        relevance: data.metrics.relevance || 0,
        helpfulness: data.metrics.helpfulness || 0,
        latency: data.metrics.latency || 0,
        projectUrl: data.metrics.project_url || ""
      }
    };
  } catch (err: any) {
    console.error("API Fetch Error:", err);
    throw new Error(err.message || "Could not connect to Aletheia Intelligence Engine.");
  }
};
