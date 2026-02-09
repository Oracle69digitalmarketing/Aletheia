
import os
import json
import asyncio
from opik import track
from typing import List, Dict, Tuple
from core.agent_utils import get_genai_client, MODELS

@track(name="planner_agent")
async def decompose_goal(goal: str) -> Tuple[List[Dict], str]:
    try:
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
            return _get_mock_tasks(goal), f"Planner Config Error: {str(e)[:50]}"

        if client is None:
            return _get_mock_tasks(goal), "Planner running in Mock Mode due to missing API keys."

        text = ""
        last_error = ""
        for m_name in MODELS:
            try:
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=m_name,
                    contents=prompt
                )
                if response and response.text:
                    text = response.text.strip()
                    if text: break
            except Exception as e:
                last_error = str(e)
                print(f"Planner Fallback: Model {m_name} failed: {e}")
                continue

        if not text:
            error_msg = str(last_error)
            if "API_KEY_INVALID" in error_msg or "401" in error_msg:
                reason = "Planner Agent: API Key Invalid. Check your GOOGLE_API_KEY."
            elif "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                reason = "Planner Agent: Rate limit exceeded. Using mock data."
            else:
                reason = f"Planner Agent: Service unavailable ({error_msg[:30]}). Using mock data."
            return _get_mock_tasks(goal), reason

        try:
            # Robust JSON extraction
            cleaned_text = text
            if "```" in cleaned_text:
                parts = cleaned_text.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"): part = part[4:].strip()
                    if part.startswith("{") and "tasks" in part:
                        cleaned_text = part
                        break
            
            # Final attempt to find JSON boundaries
            if not (cleaned_text.startswith("{") or cleaned_text.startswith("[")):
                start = cleaned_text.find("{")
                end = cleaned_text.rfind("}") + 1
                if start != -1 and end > start:
                    cleaned_text = cleaned_text[start:end]

            data = json.loads(cleaned_text)
            # Ensure it's a dict and has tasks
            if isinstance(data, dict):
                tasks = data.get("tasks", [])
                reasoning = data.get("reasoning", "Goal decomposed successfully.")
                if isinstance(tasks, list) and len(tasks) > 0:
                    return tasks, reasoning

            return _get_mock_tasks(goal), "Planner returned malformed data. Using mock tasks."
        except Exception as e:
            print(f"Planner Agent JSON Error: {e} | Raw: {text[:100]}")
            return _get_mock_tasks(goal), f"Planner Parsing Error. Using mock tasks."

    except Exception as e:
        print(f"CRITICAL Planner Agent Error: {e}")
        return _get_mock_tasks(goal), f"Critical Planner Failure: {str(e)[:50]}"

def _get_mock_tasks(goal: str) -> List[Dict]:
    return [
        {"title": "Initial Research", "description": f"Gather requirements for: {goal}", "duration": "30m"},
        {"title": "Core Strategy", "description": "Map out the primary milestones and dependencies.", "duration": "1h"},
        {"title": "First Implementation", "description": "Begin the first actionable step identified.", "duration": "2h"}
    ]

@track(name="friction_agent")
async def detect_friction(goal: str, tasks: List[Dict]) -> Tuple[str, str]:
    try:
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
            return "I'll be monitoring your progress closely.", f"Monitor Config Error: {str(e)[:30]}"

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
                if response and response.text:
                    text = response.text.strip()
                    if text: break
            except Exception as e:
                last_error = str(e)
                print(f"Monitor Fallback: Model {m_name} failed: {e}")
                continue

        if not text:
            error_msg = str(last_error)
            return "Keep going, even when it gets tough. Resilience is the key to achieving your truth.", f"Monitor Agent: Resilience active. (Error: {error_msg[:50]})"

        try:
            cleaned_text = text
            if "```" in cleaned_text:
                parts = cleaned_text.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"): part = part[4:].strip()
                    if part.startswith("{") and "intervention" in part:
                        cleaned_text = part
                        break

            if not (cleaned_text.startswith("{") or cleaned_text.startswith("[")):
                start = cleaned_text.find("{")
                end = cleaned_text.rfind("}") + 1
                if start != -1 and end > start:
                    cleaned_text = cleaned_text[start:end]

            data = json.loads(cleaned_text)
            if isinstance(data, dict):
                return data.get("intervention", "Keep pushing forward."), data.get("reasoning", "Friction detection complete.")
            return text, "Friction detection complete (text response)."
        except:
            return text[:100] if text else "Stay focused on your goal.", "Friction detection complete (fallback)."
    except Exception as e:
        print(f"CRITICAL Monitor Agent Error: {e}")
        return "The path to success is rarely a straight line. Stay persistent.", f"Critical Monitor Failure: {str(e)[:50]}"
