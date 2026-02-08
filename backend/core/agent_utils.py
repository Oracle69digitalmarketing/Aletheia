
import os
from google import genai
from opik.integrations.genai import track_genai

def get_genai_client():
    """
    Retrieves the Google GenAI client, checking for both GOOGLE_API_KEY and GEMINI_API_KEY.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not api_key or "your_" in api_key.lower():
        raise ValueError("CRITICAL: GOOGLE_API_KEY or GEMINI_API_KEY is missing or using placeholder.")

    client = genai.Client(api_key=api_key)
    return track_genai(client)
