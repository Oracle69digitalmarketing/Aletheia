
import os
from google import genai
# from opik.integrations.genai import track_genai # Opik tracking for GenAI
import openai # Assuming openai is installed

def get_llm_client():
    """
    Retrieves an LLM client (prioritizing Google Gemini, then OpenAI).
    """
    # Try Google Gemini first
    gemini_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if gemini_api_key and "your_" not in gemini_api_key.lower():
        try:
            print("Attempting to initialize Google Gemini client.")
            client = genai.Client(api_key=gemini_api_key)
            # Verify the key by trying to list models (optional but good practice)
            # client.list_models() # This might be too slow or error-prone for just init. rely on generate_content to fail.
            print("Google Gemini client initialized successfully.")
            # return track_genai(client) # Integrate Opik tracking if desired
            return {"type": "gemini", "client": client}
        except Exception as e:
            print(f"Google Gemini client initialization failed: {e}. Attempting OpenAI.")

    # Fallback to OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and "your_" not in openai_api_key.lower():
        try:
            print("Attempting to initialize OpenAI client.")
            # For newer versions of OpenAI library
            client = openai.OpenAI(api_key=openai_api_key)
            print("OpenAI client initialized successfully.")
            return {"type": "openai", "client": client}
        except Exception as e:
            print(f"OpenAI client initialization failed: {e}.")

    raise ValueError("No valid LLM client could be initialized. Please check your API keys (GOOGLE_API_KEY/GEMINI_API_KEY or OPENAI_API_KEY).")

