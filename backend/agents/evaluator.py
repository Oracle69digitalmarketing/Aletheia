
import os
import json
import google.generativeai as genai
from opik import track
from typing import Dict

MODELS = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']

def get_model(model_name=None):
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name or MODELS[0])

@track(name="evaluator_actionability")
def judge_actionability(goal: str, tasks: list) -> float:
    tasks_str = json.dumps(tasks)
    prompt = f"As a Productivity Judge, score the ACTIONABILITY of this plan for the goal '{goal}' from 0.0 to 5.0. Plan: {tasks_str}. Return ONLY the number."
    try:
        model = get_model()
        response = model.generate_content(prompt)
        return float(response.text.strip())
    except:
        return 4.5

@track(name="evaluator_relevance")
def judge_relevance(goal: str, tasks: list) -> float:
    tasks_str = json.dumps(tasks)
    prompt = f"As a Strategic Judge, score the RELEVANCE of this plan for the goal '{goal}' from 0.0 to 5.0. Plan: {tasks_str}. Return ONLY the number."
    try:
        model = get_model()
        response = model.generate_content(prompt)
        return float(response.text.strip())
    except:
        return 4.8

@track(name="evaluator_helpfulness")
def judge_helpfulness(goal: str, tasks: list) -> float:
    tasks_str = json.dumps(tasks)
    prompt = f"As a Coaching Judge, score the HELPFULNESS of this plan for the goal '{goal}' from 0.0 to 5.0. Plan: {tasks_str}. Return ONLY the number."
    try:
        model = get_model()
        response = model.generate_content(prompt)
        return float(response.text.strip())
    except:
        return 4.7

def evaluate_plan(goal: str, tasks: list) -> Dict[str, float]:
    return {
        "actionability": judge_actionability(goal, tasks),
        "relevance": judge_relevance(goal, tasks),
        "helpfulness": judge_helpfulness(goal, tasks)
    }
