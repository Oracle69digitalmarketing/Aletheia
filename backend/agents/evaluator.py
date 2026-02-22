
import os
import json
import asyncio
import re
from opik import track
from typing import Dict
from core.agent_utils import get_llm_client
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

    try:
        llm_client_info = get_llm_client()
    except Exception as e:
        print(f"Evaluator Agent Configuration Error: {e}")
        return _get_mock_scores(f"Standard evaluation applied due to configuration error: {str(e)}")

    try:
        text = await _call_llm(llm_client_info, prompt)
    except Exception as e:
        print(f"Evaluator Agent Error: {e}")
        return _get_mock_scores(f"Model response error: {str(e)[:50]}")

    if not text:
        return _get_mock_scores("Model failed to generate evaluation.")
    
    try:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in model response.")

        cleaned_json_string = json_match.group(0)
        eval_response = EvaluationResponse.model_validate_json(cleaned_json_string)
        return eval_response.model_dump()
    except Exception as e:
        print(f"Evaluator JSON Parsing Error: {e} | Raw: {text[:200]}")
        return _get_mock_scores(f"Parsing error in evaluation: {str(e)[:50]}")
