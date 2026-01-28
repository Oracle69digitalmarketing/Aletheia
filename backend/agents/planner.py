
import os
import json
import asyncio
from google import genai
from opik import track
from opik.integrations.genai import track_genai
from typing import List, Dict, Optional

# Model fallbacks for robustness
MODELS = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']

def get_model(model_name=None):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL: GOOGLE_API_KEY is missing from environment.")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name or MODELS[0])

@track(name="planner_agent")
def decompose_goal(goal: str) -> List[Dict]:
    prompt = f"""
    You are the Aletheia Planner Agent. 
    Decompose the following resolution into exactly 3 highly actionable, SMART tasks.
    Resolution: "{goal}"
    
    Return ONLY a valid JSON list of objects with keys: "title", "description", "duration".
    Do not include markdown formatting like ```json.
    """
    model = None
    for m_name in MODELS:
        try:
            model = get_model(m_name)
            response = model.generate_content(prompt)
            text = response.text.strip()
            break
        except Exception as e:
            print(f"Fallback: Model {m_name} failed: {e}")
            continue

    if not model:
        return []

    try:
        
        # Simple JSON extraction logic if model ignores instruction
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.split("```")[0].strip()
            
        return json.loads(text)
    except Exception as e:
        print(f"Planner Agent Error: {e}")
        return []

@track(name="friction_agent")
def detect_friction(goal: str, tasks: List[Dict]) -> str:
    tasks_str = ", ".join([t['title'] for t in tasks])
    prompt = f"""
    You are the Aletheia Monitor Agent. 
    Analyze this goal: "{goal}" and these tasks: {tasks_str}.
    Predict the most likely point of failure or "friction" the user will face.
    Provide a one-sentence, encouraging, yet firm intervention quote.
    """
    model = None
    for m_name in MODELS:
        try:
            model = get_model(m_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Monitor Fallback: Model {m_name} failed: {e}")
            continue

    return "I'll be monitoring your progress closely to ensure you stay on track."
