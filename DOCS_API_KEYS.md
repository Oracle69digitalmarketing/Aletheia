# Required API Keys and Environment Variables

To run Aletheia correctly, ensure the following environment variables are set.

## Backend Environment Variables (`backend/.env`)

Aletheia prioritizes LLM providers in the following order: **DeepSeek > Groq > Google/OpenAI**.

| Variable | Description |
| :--- | :--- |
| `DEEPSEEK_API_KEY` | **Recommended.** Your DeepSeek API Key. |
| `GROQ_API_KEY` | **Alternative.** Your Groq API Key. |
| `OPENAI_API_KEY` | **Fallback.** Your OpenAI API Key. |
| `OPIK_API_KEY` | **Recommended.** Your Opik/Comet API Key for tracing. (Fallback: `COMET_API_KEY`) |
| `OPIK_WORKSPACE` | Your Opik/Comet workspace name. (Fallback: `COMET_WORKSPACE`) |
| `OPIK_PROJECT_NAME` | The project name for Opik tracing. (Fallback: `OPIK_PROJECT`, `COMET_PROJECT`) |
| `MOCK_MODE` | Set to `true` to use mock agent responses (useful if no Gemini API key). |
| `DATABASE_URL` | SQLAlchemy database URL (defaults to `sqlite:///./aletheia.db`). |

## Frontend Environment Variables (`.env` or `.env.production`)

| Variable | Description |
| :--- | :--- |
| `VITE_API_URL` | The URL where your backend is hosted (e.g., `http://localhost:8000`). |

## Firebase Configuration (`services/firebase.ts`)

Currently hardcoded in `services/firebase.ts`. For production, these should ideally be moved to environment variables prefixed with `VITE_`.
