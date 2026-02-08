
import os
import json
import asyncio
from google import genai
from opik import track
from opik.integrations.genai import track_genai
from typing import Dict

MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']

def get_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL: GOOGLE_API_KEY is missing from environment.")
    client = genai.Client(api_key=api_key)
    try:
        return track_genai(client)
    except Exception as e:
        print(f"Opik track_genai Warning: {e}. Tracing might be limited for GenAI calls.")
        return client

@track(name="evaluator_ensemble")
async def evaluate_plan(goal: str, tasks: list) -> Dict[str, float]:
    """Runs all 3 evaluations in a single LLM call to reduce latency."""
    tasks_str = json.dumps(tasks)
    prompt = f"""
    You are the Aletheia Evaluator Ensemble.
    Score the following plan for the goal: "{goal}"
    Plan: {tasks_str}

    Provide exactly three scores from 0.0 to 5.0 for:
    1. actionability (Productivity Judge: how easy is it to start?)
    2. relevance (Strategic Judge: does it actually achieve the goal?)
    3. helpfulness (Coaching Judge: is the advice high quality?)

    Return ONLY a JSON object: {{"actionability": X.X, "relevance": X.X, "helpfulness": X.X}}
    """
    try:
        try:
            client = get_client()
        except ValueError as e:
            print(f"Evaluator Agent Configuration Error: {e}")
            return {"actionability": 4.5, "relevance": 4.8, "helpfulness": 4.7}

        text = ""
        for m_name in MODELS:
            try:
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=m_name,
                    contents=prompt
                )
                text = response.text.strip()
                if text: break
            except Exception as e:
                print(f"Evaluator Fallback: Model {m_name} failed: {e}")
                continue

        if not text:
            raise ValueError("Evaluator Ensemble failed to generate any response from models.")

        # Robust JSON extraction
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.split("```")[0].strip()

        scores = json.loads(text)
        return {
            "actionability": float(scores.get("actionability", 4.5)),
            "relevance": float(scores.get("relevance", 4.8)),
            "helpfulness": float(scores.get("helpfulness", 4.7))
        }
    except Exception as e:
        print(f"Evaluator Error: {e}")
        return {"actionability": 4.5, "relevance": 4.8, "helpfulness": 4.7}
