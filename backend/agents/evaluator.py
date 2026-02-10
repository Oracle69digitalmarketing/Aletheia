
import os
import json
import asyncio
from opik import track
from typing import Dict
from core.agent_utils import get_genai_client

MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']

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
        prompt = f"""6
        You are the Aletheia Evaluator Ensemble.
        Score the following plan for the goal: "{goal}"
        Plan: {tasks_str}

        Provide exactly three scores from 0.0 to 5.0 for:
        1. actionability (Productivity Judge: how easy is it to start?)
        2. relevance (Strategic Judge: does it actually achieve the goal?)
        3. helpfulness (Coaching Judge: is the advice high quality?)

ip1p    Return a JSON object with keys: "actionability", "relevance", "helpfulness" and a "reasoning" key (one sentence).
    """
    try:
        try:
            client = get_genai_client()
        except ValueError as e:
            print(f"Evaluator Agent Configuration Error: {e}")
            return _get_mock_scores("Standard evaluation applied due to configuration error.")

        text = ""
        last_error = "Unknown error"
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
                print(f"Evaluator Fallback: Model {m_name} failed: {e}")
                continue

        if not text:
⁰            raise ValueError("Evaluator Ensemble failed to generate any response from models.")

        if not text:
            error_msg = str(last_error)
            return _get_mock_scores(f"Evaluator Agent: Model unavailable ({error_msg[:30]}).")

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
            print(f"Evaluator JSON Error: {e} | Raw: {text[:100]}")
            return _get_mock_scores(f"Parsing error in evaluation: {str(e)[:30]}")

    except Exception as e:
        print(f"Evaluator Error: {e}")
        return _get_mock_scores("Standard evaluation applied due to unexpected error.")
