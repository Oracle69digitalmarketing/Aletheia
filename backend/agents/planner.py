
import os
import json
import asyncio
from opik import track
from typing import List, Dict, Tuple
from core.agent_utils import get_genai_client, MODELS

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
    except ValueError as e:
        print(f"Planner Agent Configuration Error: {e}")
        raise e

    if client is None:
        # Mock Response
        return [
            {"title": "Research initial steps", "description": f"Gather information on how to start: {goal}", "duration": "30m"},
            {"title": "Create a detailed schedule", "description": "Break down the goal into daily milestones.", "duration": "45m"},
            {"title": "Execute first milestone", "description": "Complete the first tangible task of your plan.", "duration": "1h"}
        ], "Planner running in Mock Mode due to missing API keys."

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
            print(f"Planner Fallback: Model {m_name} failed: {e}")
            continue

    if not text:
        # Fallback to Mock Mode for ANY error if all models fail
        return [
            {"title": "Research initial steps", "description": f"Gather information on how to start: {goal}", "duration": "30m"},
            {"title": "Create a detailed schedule", "description": "Break down the goal into daily milestones.", "duration": "45m"},
            {"title": "Execute first milestone", "description": "Complete the first tangible task of your plan.", "duration": "1h"}
        ], f"Planner fell back to Mock Mode. Last error: {last_error[:100]}"

    try:
        # Simple JSON extraction logic if model ignores instruction
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.split("```")[0].strip()
            
        data = json.loads(text)
        return data.get("tasks", []), data.get("reasoning", "Goal decomposed into actionable steps.")
    except Exception as e:
        print(f"Planner Agent JSON Error: {e}")
        print(f"Raw response text: {text}")
        raise e

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
    except ValueError as e:
        print(f"Monitor Agent Configuration Error: {e}")
        return "I'll be monitoring your progress closely.", "Default monitoring active."

    if client is None:
        return "Discipline is the bridge between goals and accomplishment.", "Monitor running in Mock Mode."

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
        # Fallback to Mock Mode for ANY error
        return "Keep going, even when it gets tough. Resilience is the key to achieving your truth.", f"Monitor fell back to Mock Mode. Last error: {last_error[:100]}"

    try:
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.split("```")[0].strip()
        data = json.loads(text)
        return data.get("intervention", ""), data.get("reasoning", "Friction detection complete.")
    except:
        return text, "Friction detection complete."
