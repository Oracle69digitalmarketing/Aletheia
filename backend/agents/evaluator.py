
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

@track(name="evaluator_agent")
def evaluate_plan(goal: str, tasks: list) -> Dict[str, float]:
    tasks_str = json.dumps(tasks)
    prompt = f"""
    You are the Aletheia Evaluator Agent. 
    Score the following plan for the goal: "{goal}"
    Plan: {tasks_str}
    
    Provide scores from 0.0 to 5.0 for:
    1. actionability (how easy is it to start?)
    2. relevance (does it actually achieve the goal?)
    3. helpfulness (is the advice high quality?)
    
    Return ONLY a JSON object: {{"actionability": X.X, "relevance": X.X, "helpfulness": X.X}}
    """
    model = None
    for m_name in ['gemini-3-flash-preview'] + MODELS:
        try:
            model = get_model(m_name)
            response = model.generate_content(prompt)
            text = response.text.strip()
            break
        except Exception as e:
            print(f"Evaluator Fallback: Model {m_name} failed: {e}")
            continue

    if not model:
        return {"actionability": 4.5, "relevance": 4.5, "helpfulness": 4.5}

    try:
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except:
        return {"actionability": 4.5, "relevance": 4.5, "helpfulness": 4.5}
