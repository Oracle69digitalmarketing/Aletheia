
import os
import json
import asyncio
import re # Import re for regex
from opik import track
from typing import List, Dict, Tuple
from core.agent_utils import get_genai_client
from pydantic import BaseModel, Field # Import BaseModel and Field
from models import Task, AgentThought # Import Task and AgentThought

# Model fallbacks for robustness
MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']

class PlannerResponse(BaseModel):
    tasks: List[Task] = Field(..., description="A list of 3 objects with keys: 'title', 'description', 'duration'.")
    reasoning: str = Field(..., description="A one-sentence professional explanation of your planning logic.")

class FrictionResponse(BaseModel):
    intervention: str = Field(..., description="A one-sentence, encouraging, yet firm intervention quote.")
    reasoning: str = Field(..., description="A one-sentence explanation of why you chose this intervention.")

@track(name="planner_agent")
async def decompose_goal(goal: str) -> Tuple[List[Dict], str]:
    prompt = f"""
    You are the Aletheia Planner Agent. 
    Decompose the following resolution into exactly 3 highly actionable, SMART tasks.
    Resolution: "{goal}"
    
    Return a JSON object with two keys:
    1. "tasks": A list of 3 objects with keys: "title", "description", "duration".
    2. "reasoning": A one-sentence professional explanation of your planning logic.

    Do not include markdown formatting like ```json.
    """
    try:
        client = get_genai_client()
    except Exception as e:
        print(f"Planner Agent Configuration Error: {e}")
        return [], f"Configuration Error: {str(e)}"

    text = ""
    last_error = ""
    for m_name in MODELS:
        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=m_name,
                contents=prompt
            )
            text = response.text.strip()
            if text:
                break
        except Exception as e:
            last_error = str(e)
            print(f"Planner Fallback: Model {m_name} failed: {e}")
            continue

    if not text:
        print("Planner Agent Error: All models failed to generate tasks.")
        return [], f"Model Error: All models failed. Last error: {last_error}"

    try:
        # Use regex to find the JSON object more robustly
        # This looks for content between the first { and last }
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in model response.")
            
        cleaned_json_string = json_match.group(0)
        
        # Use Pydantic for parsing and validation
        planner_response = PlannerResponse.model_validate_json(cleaned_json_string)
        
        # The Task model in main.py has default values for id, status, category
        # If the LLM returns only title, description, duration, Pydantic will fill the rest.
        return [task.model_dump() for task in planner_response.tasks], planner_response.reasoning
    except Exception as e:
        print(f"Planner Agent JSON Error: {e}")
        print(f"Raw response text: {text}")
        return [], f"Parsing Error: Could not decode or validate model response. {str(e)}"

@track(name="friction_agent")
async def detect_friction(goal: str, tasks: List[Dict]) -> Tuple[str, str]:
    tasks_str = ", ".join([t.get('title', 'Unknown Task') for t in tasks])
    prompt = f"""
    You are the Aletheia Monitor Agent. 
    Analyze this goal: "{goal}" and these tasks: {tasks_str}.
    Predict the most likely point of failure or "friction" the user will face.

    Return a JSON object with:
    1. "intervention": A one-sentence, encouraging, yet firm intervention quote.
    2. "reasoning": A one-sentence explanation of why you chose this intervention.
    """
    try:
        client = get_genai_client()
    except Exception as e:
        print(f"Monitor Agent Configuration Error: {e}")
        return "I'll be monitoring your progress closely.", "Default monitoring active due to configuration error."

    text = ""
    last_error = ""
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
            last_error = str(e)
            print(f"Monitor Fallback: Model {m_name} failed: {e}")
            continue

    if not text:
        return "I'll be monitoring your progress closely to ensure you stay on track.", "Standard fallback intervention used."

    try:
        # Use regex to find the JSON object more robustly
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in model response.")
            
        cleaned_json_string = json_match.group(0)
        
        # Use Pydantic for parsing and validation
        friction_response = FrictionResponse.model_validate_json(cleaned_json_string)
        
        return friction_response.intervention, friction_response.reasoning
    except Exception as e:
        print(f"Monitor Agent JSON Error: {e}")
        print(f"Raw response text: {text}")
        return "I'll be monitoring your progress closely (parsing failed).", f"Parsing Error: Could not decode or validate model response. {str(e)}"
