import os
import openai

def get_llm_client():
    """
    Retrieves an LLM client (OpenAI).
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and "your_" not in openai_api_key.lower():
        try:
            print("Attempting to initialize OpenAI client.")
            client = openai.OpenAI(api_key=openai_api_key)
            print("OpenAI client initialized successfully.")
            return {"type": "openai", "client": client}
        except Exception as e:
            print(f"OpenAI client initialization failed: {e}.")

    raise ValueError("No valid LLM client could be initialized. Please check your OPENAI_API_KEY.")
