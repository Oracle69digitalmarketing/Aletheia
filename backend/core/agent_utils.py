import os
from openai import OpenAI

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def get_all_llm_clients():
    """
    Returns a list of all available LLM configurations based on environment variables.
    Each config is a dictionary: {'type': str, 'client': object, 'model': str}
    """
    clients = []

    # 1. DeepSeek
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_api_key and "your_" not in deepseek_api_key.lower():
        try:
            client = openai.OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
            clients.append({"type": "deepseek", "client": client, "model": "deepseek-chat"})
        except Exception as e:
            print(f"DeepSeek initialization failed: {e}")

    # 2. Groq
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and "your_" not in groq_api_key.lower():
        try:
            client = openai.OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
            clients.append({"type": "groq", "client": client, "model": "llama-3.3-70b-versatile"})
        except Exception as e:
            print(f"Groq initialization failed: {e}")

    # 3. OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and "your_" not in openai_api_key.lower():
        try:
            client = openai.OpenAI(api_key=openai_api_key)
            clients.append({"type": "openai", "client": client, "model": "gpt-4o"})
        except Exception as e:
            print(f"OpenAI initialization failed: {e}")

    # 4. Google Gemini
    google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if google_api_key and "your_" not in google_api_key.lower() and HAS_GENAI:
        try:
            client = genai.Client(api_key=google_api_key)
            clients.append({"type": "gemini", "client": client, "model": "gemini-1.5-flash"})
        except Exception as e:
            print(f"Gemini initialization failed: {e}")

    return clients

def get_llm_client():
    """
    Retrieves the primary LLM client. Included for backward compatibility.
    """
    clients = get_all_llm_clients()
    if not clients:
        raise ValueError("No valid LLM client could be initialized. Please check your API keys.")
    return clients[0]
