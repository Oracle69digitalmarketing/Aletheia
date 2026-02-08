
import os
from google import genai
from opik.integrations.genai import track_genai

# Centralized model list with fallbacks
MODELS = [
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash-002',
    'gemini-1.5-pro',
    'gemini-1.5-flash-8b'
]

def get_genai_client():
    """
    Retrieves the Google GenAI client, checking for both GOOGLE_API_KEY and GEMINI_API_KEY.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    # Check for placeholder or missing key
    is_placeholder = api_key and "your_" in api_key.lower()
    if not api_key or is_placeholder:
        # If we are in "MOCK_MODE" or just missing keys, we might want to return None
        # and let the agents handle it with mock data instead of crashing.
        if os.getenv("MOCK_MODE", "true").lower() == "true" or is_placeholder:
            return None
        raise ValueError("CRITICAL: GOOGLE_API_KEY or GEMINI_API_KEY is missing or using placeholder. Set MOCK_MODE=true to bypass.")

    try:
        # Try to use v1 for better compatibility with 1.5 models if v1beta fails
        client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
        return track_genai(client)
    except Exception as e:
        print(f"GenAI Client Init Warning: {e}")
        client = genai.Client(api_key=api_key)
        return track_genai(client)
