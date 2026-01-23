
import os
import json
import google.generativeai as genai
from opik import track
from typing import List, Dict, Optional

# Single source of truth for the model name
DEFAULT_MODEL = 'gemini-3-flash-preview'

def get_model():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL: GOOGLE_API_KEY is missing from environment.")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(DEFAULT_MODEL)

@track(name="planner_agent")
def decompose_goal(goal: str) -> List[Dict]:
    model = get_model()
    prompt = f"""
    You are the Aletheia Planner Agent. 
    Decompose the following resolution into exactly 3 highly actionable, SMART tasks.
    Resolution: "{goal}"
    
    Return ONLY a valid JSON list of objects with keys: "title", "description", "duration".
    Do not include markdown formatting like ```json.
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
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
    model = get_model()
    tasks_str = ", ".join([t['title'] for t in tasks])
    prompt = f"""
    You are the Aletheia Monitor Agent. 
    Analyze this goal: "{goal}" and these tasks: {tasks_str}.
    Predict the most likely point of failure or "friction" the user will face.
    Provide a one-sentence, encouraging, yet firm intervention quote.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Monitor Agent Error: {e}")
        return "I'll be monitoring your progress closely to ensure you stay on track."
