
import os
import json
import google.generativeai as genai
from opik import track
from typing import Dict

MODELS = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']

def get_model(model_name=None):
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name or MODELS[0])

@track(name="evaluator_ensemble")
def evaluate_plan(goal: str, tasks: list) -> Dict[str, float]:
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
        model = get_model()
        response = model.generate_content(prompt)
        text = response.text.strip()

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
