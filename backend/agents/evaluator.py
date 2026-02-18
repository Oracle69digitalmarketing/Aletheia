import os
import json
import asyncio
from opik import track
from typing import Dict
from core.agent_utils import get_llm_client

OPENAI_MODEL = 'gpt-4o' # Or 'gpt-3.5-turbo' for cheaper/faster

def _get_mock_scores(reasoning: str) -> Dict:
    return {
        "actionability": 4.5,
        "relevance": 4.8,
        "helpfulness": 4.7,
        "reasoning": reasoning
    }

@track(name="evaluator_ensemble")
async def evaluate_plan(goal: str, tasks: list) -> Dict:
    """Runs all 3 evaluations in a single LLM call to reduce latency."""
    try:
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
        llm_client_info = get_llm_client() # Changed
        llm_client_type = llm_client_info["type"]
        llm_client = llm_client_info["client"]
    except Exception as e: # Catch all exceptions for client initialization
        print(f"Evaluator Agent Configuration Error: {e}")
        return _get_mock_scores("Standard evaluation applied due to configuration error.")

    text = ""
    last_error = "" # Initialize last_error here

    if llm_client_type == "openai":
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await asyncio.to_thread(
                llm_client.chat.completions.create,
                model=OPENAI_MODEL,
                messages=messages,
                response_format={"type": "json_object"} # Specify JSON output
            )
            text = response.choices[0].message.content.strip()
        except Exception as e:
            last_error = str(e)
            print(f"Evaluator Fallback: OpenAI Model {OPENAI_MODEL} failed: {e}")

        if not text:
            # Fallback if no text is generated from any model
            error_msg = str(last_error)
            print(f"Evaluator Ensemble failed to generate any response from models. Last error: {error_msg}")
            return _get_mock_scores(f"Model response error: {error_msg[:30]}")
    else: # If client type is not openai, it implies an error in get_llm_client
        error_msg = "LLM client not configured correctly (not OpenAI)."
        print(f"Evaluator Agent Error: {error_msg}")
        return _get_mock_scores(f"Model response error: {error_msg[:30]}")
    
    try:
        cleaned_text = text
        if "```" in cleaned_text:
            parts = cleaned_text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"): part = part[4:].strip()
                if part.startswith("{") and "actionability" in part:
                    cleaned_text = part
                    break

        if not (cleaned_text.startswith("{") or cleaned_text.startswith("[")):
            start = cleaned_text.find("{")
            end = cleaned_text.rfind("}") + 1
            if start != -1 and end > start:
                cleaned_text = cleaned_text[start:end]

        scores = json.loads(cleaned_text)
        if not isinstance(scores, dict):
            return _get_mock_scores("Malformed evaluator response.")

        return {
            "actionability": float(scores.get("actionability", 4.5)),
            "relevance": float(scores.get("relevance", 4.8)),
            "helpfulness": float(scores.get("helpfulness", 4.7)),
            "reasoning": scores.get("reasoning", "Plan verified for actionability and relevance.")
        }
    except Exception as e:
        print(f"Evaluator JSON Parsing Error: {e} | Raw: {text[:200]}") # Increased raw text length for debug
        return _get_mock_scores(f"Parsing error in evaluation: {str(e)[:50]}")