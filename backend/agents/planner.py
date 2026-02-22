
import os
import json
import asyncio
import re
from opik import track
from typing import List, Dict, Tuple
from core.agent_utils import get_llm_client
from pydantic import BaseModel, Field
from models import Task, AgentThought

class PlannerResponse(BaseModel):
    tasks: List[Task] = Field(..., description="A list of 3 objects with keys: 'title', 'description', 'duration'.")
    reasoning: str = Field(..., description="A one-sentence professional explanation of your planning logic.")

class FrictionResponse(BaseModel):
    intervention: str = Field(..., description="A one-sentence, encouraging, yet firm intervention quote.")
    reasoning: str = Field(..., description="A one-sentence explanation of why you chose this intervention.")

async def _call_llm(client_info, prompt, response_model):
    llm_client = client_info["client"]
    llm_model = client_info["model"]
    llm_type = client_info["type"]

    if llm_type == "gemini":
        response = await asyncio.to_thread(
            llm_client.models.generate_content,
            model=llm_model,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return response.text
    else:
        extra_args = {}
        if llm_type in ["openai", "deepseek", "groq"]:
            extra_args["response_format"] = {"type": "json_object"}

        messages = [{"role": "user", "content": prompt}]
        response = await asyncio.to_thread(
            llm_client.chat.completions.create,
            model=llm_model,
            messages=messages,
            **extra_args
        )
        return response.choices[0].message.content

@track(name="planner_agent")
async def decompose_goal(goal: str) -> Tuple[List[Dict], str]:
    prompt = f"""
    You are the Aletheia Planner Agent.
    Decompose the following resolution into exactly 3 highly actionable, SMART tasks.
    Resolution: "{goal}"

    Return a JSON object with two keys:
    1. "tasks": A list of 3 objects with keys: "title", "description", "duration".
    2. "reasoning": A one-sentence professional explanation of your planning logic.
    """
    try:
        llm_client_info = get_llm_client()
    except Exception as e:
        print(f"Planner Agent Configuration Error: {e}")
        return [], f"Configuration Error: {str(e)}"

    try:
        text = await _call_llm(llm_client_info, prompt, PlannerResponse)
    except Exception as e:
        print(f"Planner Agent Error: {e}")
        return [], f"Model Error: {str(e)}"

    if not text:
        return [], "Model Error: All models failed to generate tasks."

    try:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in model response.")
            
        cleaned_json_string = json_match.group(0)
        planner_response = PlannerResponse.model_validate_json(cleaned_json_string)
        return [task.model_dump() for task in planner_response.tasks], planner_response.reasoning
    except Exception as e:
        print(f"Planner Agent JSON Error: {e}")
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
        llm_client_info = get_llm_client()
    except Exception as e:
        print(f"Monitor Agent Configuration Error: {e}")
        return "I'll be monitoring your progress closely.", "Default monitoring active due to configuration error."

    try:
        text = await _call_llm(llm_client_info, prompt, FrictionResponse)
    except Exception as e:
        print(f"Monitor Agent Error: {e}")
        return "I'll be monitoring your progress closely to ensure you stay on track.", "Standard fallback intervention used due to model error."

    if not text:
        return "I'll be monitoring your progress closely to ensure you stay on track.", "Standard fallback intervention used."

    try:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in model response.")
            
        cleaned_json_string = json_match.group(0)
        friction_response = FrictionResponse.model_validate_json(cleaned_json_string)
        return friction_response.intervention, friction_response.reasoning
    except Exception as e:
        return "I'll be monitoring your progress closely (parsing failed).", f"Parsing Error: Could not decode or validate model response. {str(e)}"
