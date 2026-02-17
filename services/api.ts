
import { Plan, TaskStatus, LogEntry } from "../types";

/**
 * PRODUCTION SETUP:
 * Replace the string below with your actual Render backend URL 
 * (e.g., https://aletheia-backend.onrender.com)
 */
const PRODUCTION_API_URL = "https://aletheia-backend-yu1n.onrender.com";

const API_URL = import.meta.env.VITE_API_URL || PRODUCTION_API_URL;

export const generateAgenticPlan = async (goal: string): Promise<Plan> => {
  // Add a trailing slash check or ensure consistency
  const baseUrl = API_URL.replace(/\/$/, '');
  const endpoint = `${baseUrl}/api/plan`;
  
  // Create an AbortController for a 30s timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Service Unreachable' }));
      throw new Error(errorData.detail || `Server responded with ${response.status}`);
    }

    const data = await response.json().catch(() => null);

    if (!data || !data.tasks) {
      throw new Error("Invalid response format from Aletheia Engine.");
    }

    const logs: LogEntry[] = [
      { id: '1', timestamp: new Date().toLocaleTimeString(), level: 'INFO', source: 'SYSTEM', message: `POST /api/plan 200 OK` },
      { id: '2', timestamp: new Date().toLocaleTimeString(), level: 'TRACE', source: 'OPIK', message: `Trace ID [${data.traceId || 'N/A'}] synchronized.` },
      { id: '3', timestamp: new Date().toLocaleTimeString(), level: 'DEBUG', source: 'EVALUATOR', message: `Scoring complete: Rel ${data.metrics?.relevance || 'N/A'}` },
    ];

    return {
      id: data.id || Math.random().toString(36).substr(2, 8),
      originalGoal: goal,
      category: data.category || "General",
      tasks: (data.tasks || []).map((t: any) => ({
        ...t,
        id: t.id || Math.random().toString(36).substr(2, 9),
        status: TaskStatus.TODO,
        category: data.category || "General"
      })),
      agentReasoning: (data.agentReasoning || []).map((r: any) => ({
        ...r,
        timestamp: new Date().toLocaleTimeString()
      })),
      traceId: data.traceId || "",
      traceUrl: data.traceUrl || "",
      logs: logs,
      frictionIntervention: data.frictionIntervention || "No friction detected.",
      metrics: {
        actionability: data.metrics?.actionability ?? 0,
        relevance: data.metrics?.relevance ?? 0,
        helpfulness: data.metrics?.helpfulness ?? 0,
        latency: data.metrics?.latency ?? 0,
        projectUrl: data.metrics?.projectUrl ?? ""
      }
    };
  } catch (err: any) {
    console.error("API Fetch Error:", err);
    throw new Error(err.message || "Could not connect to Aletheia Intelligence Engine.");
  }
};
