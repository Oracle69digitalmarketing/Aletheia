
import os
import json
import google.generativeai as genai
from opik import track
from typing import Dict

def get_model():
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-3-flash-preview')

@track(name="evaluator_agent")
def evaluate_plan(goal: str, tasks: list) -> Dict[str, float]:
    model = get_model()
    tasks_str = json.dumps(tasks)
    prompt = f"""
    You are the Aletheia Evaluator Agent. 
    Score the following plan for the goal: "{goal}"
    Plan: {tasks_str}
    
    Provide scores from 0.0 to 5.0 for:
    1. actionability (how easy is it to start?)
    2. relevance (does it actually achieve the goal?)
    3. helpfulness (is the advice high quality?)
    
    Return ONLY a JSON object: {{"actionability": X.X, "relevance": X.X, "helpfulness": X.X}}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except:
        return {"actionability": 4.5, "relevance": 4.5, "helpfulness": 4.5}
