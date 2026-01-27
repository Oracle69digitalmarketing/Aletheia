
import os
import sys
# Ensure the backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import AnswerRelevance, Hallucination
from agents.planner import decompose_goal
from dotenv import load_dotenv

load_dotenv()

# 1. Define the evaluation task
def evaluation_task(x):
    # x is an item from our dataset
    goal = x['goal']
    result = decompose_goal(goal)
    # Return the result in a format that metrics can use
    # Most Opik metrics expect 'output' and 'input' or 'context'
    return {
        "output": str(result),
        "input": goal
    }

# 2. Define the dataset
dataset = [
    {"goal": "Learn Python in 30 days"},
    {"goal": "Run a 5k marathon next month"},
    {"goal": "Build a SaaS product in a weekend"},
    {"goal": "Master meditation and mindfulness"},
    {"goal": "Lose 5kg by eating healthy"}
]

# 3. Define metrics (3 evaluators as requested)
relevance_metric = AnswerRelevance()
# We can also add custom metrics or other built-ins
# For this example, we'll use Hallucination and a custom heuristic

def actionability_metric(output, **kwargs):
    # Simple heuristic: more tasks = more actionable?
    # Or just check if it's a list
    try:
        import json
        tasks = eval(output)
        if isinstance(tasks, list) and len(tasks) > 0:
            return 1.0
    except:
        pass
    return 0.0

def main():
    print("Starting Aletheia Opik Evaluation...")

    # Run evaluation
    res = evaluate(
        dataset=dataset,
        task=evaluation_task,
        metrics=[relevance_metric, Hallucination(), actionability_metric],
        experiment_name="Aletheia Planning Experiment v1"
    )

    print("Evaluation Complete!")
    print(res)

if __name__ == "__main__":
    main()
