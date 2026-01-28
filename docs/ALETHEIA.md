# Aletheia Documentation

Welcome to Aletheia, your Agentic AI Accountability Co-pilot.

## Features

- **Goal Decomposition**: Our Planner agent takes your New Year's resolutions and breaks them down into actionable steps.
- **Agentic Ensemble**: Multiple AI agents (Planner, Orchestrator, Evaluator, Monitor) work together to ensure your plan is robust.
- **Real-Time Tracing**: Powered by Comet Opik, every thought process of our agents is visible in real-time.
- **Friction Detection**: Our Monitor agent identifies potential obstacles and suggests interventions.

## Getting Started

1. **Connect Your Account**: Sign in with Google, GitHub, or Twitter to personalize your experience.
2. **Set a Goal**: Type your resolution in the input box.
3. **Generate Strategy**: Click "Generate" and watch our agents work.
4. **Track Progress**: Use the Strategy View to mark tasks as completed.
5. **Analyze Logic**: Check the Opik Trace Viewer to see the agents' reasoning.

## Technology Stack

- **Frontend**: Next.js 15, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **AI**: Google Gemini API, LangChain
- **Observability**: Comet Opik
- **Auth**: Firebase Authentication

## Opik Comet Integration

Aletheia uses Comet Opik for agent observability. To configure your own workspace, you need the following keys:

1. **Environment Variables**:
   Set these in your backend `.env` file or deployment environment (e.g., Render settings):
   - `GOOGLE_API_KEY`: Required for Gemini model access.
   - `OPIK_API_KEY`: Required for authenticating with the Opik platform (grab this from your Comet account).
   - `OPIK_PROJECT_NAME`: (Optional) The name of your project in Opik (e.g., `aletheia-hackathon`).
   - `COMET_WORKSPACE`: (Optional) Your Comet workspace name.

2. **Automatic Tracing**:
   All agent interactions are automatically tracked using the `@track` decorator. Traces are pushed asynchronously to the Comet dashboard.

3. **LLM-as-Judge**:
   The `Evaluator Ensemble` runs as a tracked span, scoring every plan on Actionability, Relevance, and Helpfulness. These scores are synced back to the main trace for performance comparison.
