
import os
import json
import asyncio
from google import genai
from opik import track
from opik.integrations.genai import track_genai
from typing import List, Dict, Optional

# Model fallbacks for robustness
MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']

def get_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL: GOOGLE_API_KEY is missing from environment.")
    client = genai.Client(api_key=api_key)
    return track_genai(client)

@track(name="planner_agent")
async def decompose_goal(goal: str) -> List[Dict]:
    prompt = f"""
    You are the Aletheia Planner Agent. 
    Decompose the following resolution into exactly 3 highly actionable, SMART tasks.
    Resolution: "{goal}"
    
    Return ONLY a valid JSON list of objects with keys: "title", "description", "duration".
    Do not include markdown formatting like ```json.
    """
    try:
        client = get_client()
    except ValueError as e:
        print(f"Planner Agent Configuration Error: {e}")
        return []

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
            print(f"Planner Fallback: Model {m_name} failed: {e}")
            continue

    if not text:
        print("Planner Agent Error: All models failed to generate tasks.")
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
        print(f"Planner Agent JSON Error: {e}")
        print(f"Raw response text: {text}")
        return []

@track(name="friction_agent")
async def detect_friction(goal: str, tasks: List[Dict]) -> str:
    tasks_str = ", ".join([t['title'] for t in tasks])
    prompt = f"""
    You are the Aletheia Monitor Agent. 
    Analyze this goal: "{goal}" and these tasks: {tasks_str}.
    Predict the most likely point of failure or "friction" the user will face.
    Provide a one-sentence, encouraging, yet firm intervention quote.
    """
    try:
        client = get_client()
    except ValueError as e:
        print(f"Monitor Agent Configuration Error: {e}")
        return "I'll be monitoring your progress closely."

    for m_name in MODELS:
        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=m_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Monitor Fallback: Model {m_name} failed: {e}")
            continue

    return "I'll be monitoring your progress closely to ensure you stay on track."
