import os
import openai
from google import genai
from google.genai import types

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def get_all_llm_clients():
    """
    Retrieves an LLM client, prioritizing DeepSeek, then Groq, then OpenAI, then Google Gemini.
    Returns a dictionary with 'type', 'client', and 'model'.
    """
    # 1. DeepSeek
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_api_key and "your_" not in deepseek_api_key.lower():
        try:
            print("Attempting to initialize DeepSeek client.")
            client = openai.OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
            print("DeepSeek client initialized successfully.")
            return {"type": "deepseek", "client": client, "model": "deepseek-chat"}
        except Exception as e:
            print(f"DeepSeek client initialization failed: {e}.")

    # 2. Groq
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and "your_" not in groq_api_key.lower():
        try:
            print("Attempting to initialize Groq client.")
            client = openai.OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
            print("Groq client initialized successfully.")
            return {"type": "groq", "client": client, "model": "llama-3.3-70b-versatile"}
        except Exception as e:
            print(f"Groq client initialization failed: {e}.")

    # 3. OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and "your_" not in openai_api_key.lower():
        try:
            client = openai.OpenAI(api_key=openai_api_key)
            print("OpenAI client initialized successfully.")
            return {"type": "openai", "client": client, "model": "gpt-4o"}
        except Exception as e:
            print(f"Gemini initialization failed: {e}")

    # 4. Google Gemini (Fallback)
    google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if google_api_key and "your_" not in google_api_key.lower():
        try:
            print("Attempting to initialize Google Gemini client.")
            # Wrap Gemini in an OpenAI-compatible interface if possible, or handle separately.
            # For now, we will return the genai client but the agents need to handle it.
            # Since agents expect chat.completions.create, we might need a wrapper.
            # To keep it simple and consistent with existing code, let's use the genai client
            # and let agents handle the 'gemini' type.
            client = genai.Client(api_key=google_api_key)
            print("Google Gemini client initialized successfully.")
            return {"type": "gemini", "client": client, "model": "gemini-1.5-flash"}
        except Exception as e:
            print(f"Google Gemini client initialization failed: {e}.")

    raise ValueError("No valid LLM client could be initialized. Please check your DEEPSEEK_API_KEY, GROQ_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY.")
