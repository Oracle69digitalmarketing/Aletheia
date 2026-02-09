
import os
from google import genai
from opik.integrations.genai import track_genai
from core.opik_setup import get_project

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
    Retrieves the Google GenAI client.
    Supports both GOOGLE_API_KEY and GEMINI_API_KEY (from Google AI Studio / Gemini Studio).
    """
    raw_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not raw_key:
        if os.getenv("MOCK_MODE", "true").lower() == "true":
            return None
        raise ValueError("CRITICAL: GOOGLE_API_KEY or GEMINI_API_KEY is missing. Set MOCK_MODE=true to bypass.")

    # Sanitize Key: strip whitespace and any surrounding quotes that might have been added in Render/Vercel
    api_key = raw_key.strip().strip('"').strip("'")

    # Check for placeholder
    if "your_" in api_key.lower() or "api_key" in api_key.lower():
        if os.getenv("MOCK_MODE", "true").lower() == "true":
            print(f"Placeholder API Key detected ({api_key[:4]}...). Using Mock Mode.")
            return None
        raise ValueError(f"CRITICAL: API Key appears to be a placeholder: {api_key[:8]}...")

    try:
        # Try to use v1 for better compatibility with 1.5 models if v1beta fails
        # Using the sanitized key
        client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
        return track_genai(client, project_name=get_project())
    except Exception as e:
        print(f"GenAI Client Init Warning (v1 failed): {e}")
        client = genai.Client(api_key=api_key)
        return track_genai(client, project_name=get_project())
