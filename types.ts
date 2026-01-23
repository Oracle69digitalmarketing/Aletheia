
export enum TaskStatus {
  TODO = 'todo',
  IN_PROGRESS = 'in-progress',
  COMPLETED = 'completed',
  BLOCKED = 'blocked'
}

export interface Task {
  id: string;
  title: string;
  description: string;
  duration: string;
  status: TaskStatus;
  category: string;
}

export interface AgentReasoning {
  agent: 'Planner' | 'Orchestrator' | 'Evaluator' | 'Monitor';
  thought: string;
  timestamp: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'INFO' | 'TRACE' | 'DEBUG' | 'WARN';
  source: string;
  message: string;
}

export interface User {
  name: string;
  email: string;
  avatar?: string;
  connectedAt: string;
}

export interface Plan {
  id: string;
  originalGoal: string;
  category: string;
  tasks: Task[];
  agentReasoning: AgentReasoning[];
  traceId: string;
  traceUrl: string;
  logs: LogEntry[];
  frictionIntervention: string;
  metrics: {
    actionability: number;
    relevance: number;
    helpfulness: number;
    latency: number;
    projectUrl?: string;
  };
}
