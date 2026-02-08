
import os
from dotenv import load_dotenv

load_dotenv()

def get_workspace():
    return os.getenv("OPIK_WORKSPACE", "oracle69digitalmarketing")

def get_project():
    return os.getenv("OPIK_PROJECT") or os.getenv("COMET_PROJECT") or "aletheia-hackathon"

def get_trace_url(trace_id: str):
    workspace = get_workspace()
    project = get_project()
    # Updated to the standard Opik trace URL format
    return f"https://www.comet.com/{workspace}/opik/projects/{project}/traces/{trace_id}"

def get_project_url():
    workspace = get_workspace()
    project = get_project()
    return f"https://www.comet.com/{workspace}/opik/projects/{project}/dashboard"
