# Required API Keys and Environment Variables

To run Aletheia correctly, ensure the following environment variables are set.

## Backend Environment Variables (`backend/.env`)

Aletheia prioritizes LLM providers in the following order: **DeepSeek > Groq > OpenAI > Google**.

| Variable | Description |
| :--- | :--- |
| `DEEPSEEK_API_KEY` | **Recommended.** Your API key from DeepSeek. Uses `deepseek-chat` model. |
| `GROQ_API_KEY` | **Recommended.** Your API key from Groq. Uses `llama-3.3-70b-versatile` model. |
| `OPENAI_API_KEY` | Your OpenAI API key. Uses `gpt-4o`. |
| `GOOGLE_API_KEY` | Your API key from Google AI Studio / Gemini Studio. (Fallback: `GEMINI_API_KEY`). Uses `gemini-1.5-flash`. |
| `OPIK_API_KEY` | **Recommended.** Your Opik/Comet API Key for tracing. |
| `OPIK_WORKSPACE` | Your Opik/Comet workspace name. |
| `OPIK_PROJECT_NAME` | The project name for Opik tracing. |
| `DATABASE_URL` | SQLAlchemy database URL (defaults to `sqlite:///./aletheia.db`). |

## Frontend Environment Variables (`.env` or `.env.production`)

| Variable | Description |
| :--- | :--- |
| `VITE_API_URL` | The URL where your backend is hosted (e.g., `http://localhost:8000`). |

## Firebase Configuration (`services/firebase.ts`)

Currently hardcoded in `services/firebase.ts`. For production, these should ideally be moved to environment variables prefixed with `VITE_`.
