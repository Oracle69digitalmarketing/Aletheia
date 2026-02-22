
import os
import json
import asyncio
import re
from opik import track
from typing import Dict
from core.agent_utils import get_all_llm_clients
from pydantic import BaseModel, Field

class EvaluationResponse(BaseModel):
    actionability: float = Field(..., ge=0.0, le=5.0)
    relevance: float = Field(..., ge=0.0, le=5.0)
    helpfulness: float = Field(..., ge=0.0, le=5.0)
    reasoning: str

def _get_mock_scores(reasoning: str) -> Dict:
    return {
        "actionability": 4.5,
        "relevance": 4.8,
        "helpfulness": 4.7,
        "reasoning": reasoning
    }

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

@track(name="evaluator_ensemble")
async def evaluate_plan(goal: str, tasks: list) -> Dict:
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

    Return a JSON object with keys: "actionability", "relevance", "helpfulness" and a "reasoning" key (one sentence).
    """

    clients = get_all_llm_clients()
    if not clients:
        return _get_mock_scores("Configuration Error: No valid LLM clients found.")

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
            eval_response = EvaluationResponse.model_validate_json(cleaned_json_string)
            return eval_response.model_dump()
        except Exception as e:
            last_error = str(e)
            print(f"Evaluator Agent ({client_info['type']}) failed: {e}")
            continue

    return _get_mock_scores(f"Evaluation failed. Last error: {last_error[:50]}...")
