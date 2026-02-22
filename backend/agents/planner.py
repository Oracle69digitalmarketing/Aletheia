
import os
import json
import asyncio
import re
from opik import track
from typing import List, Dict, Tuple
from core.agent_utils import get_all_llm_clients
from pydantic import BaseModel, Field
from models import Task, AgentThought

class PlannerResponse(BaseModel):
    tasks: List[Task] = Field(..., description="A list of 3 objects with keys: 'title', 'description', 'duration'.")
    reasoning: str = Field(..., description="A one-sentence professional explanation of your planning logic.")

class FrictionResponse(BaseModel):
    intervention: str = Field(..., description="A one-sentence, encouraging, yet firm intervention quote.")
    reasoning: str = Field(..., description="A one-sentence explanation of why you chose this intervention.")

async def _call_llm(client_info, prompt):
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
    clients = get_all_llm_clients()
    if not clients:
        return [], "Configuration Error: No valid LLM clients found."

    last_error = ""
    for client_info in clients:
        try:
            text = await _call_llm(client_info, prompt)
            if not text:
                continue

            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if not json_match:
                continue

            cleaned_json_string = json_match.group(0)
            planner_response = PlannerResponse.model_validate_json(cleaned_json_string)
            return [task.model_dump() for task in planner_response.tasks], planner_response.reasoning
        except Exception as e:
            last_error = str(e)
            print(f"Planner Agent ({client_info['type']}) failed: {e}")
            continue

    return [], f"Model Error: All models failed. Last error: {last_error}"

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
    clients = get_all_llm_clients()
    if not clients:
        return "I'll be monitoring your progress closely.", "Default monitoring active due to configuration error."

    last_error = ""
    for client_info in clients:
        try:
            text = await _call_llm(client_info, prompt)
            if not text:
                continue

            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if not json_match:
                continue

            cleaned_json_string = json_match.group(0)
            friction_response = FrictionResponse.model_validate_json(cleaned_json_string)
            return friction_response.intervention, friction_response.reasoning
        except Exception as e:
            last_error = str(e)
            print(f"Monitor Agent ({client_info['type']}) failed: {e}")
            continue

    return "I'll be monitoring your progress closely to ensure you stay on track.", f"Standard fallback used. Last error: {last_error}"
