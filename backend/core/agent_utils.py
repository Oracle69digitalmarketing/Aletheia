import os
import openai

def get_llm_client():
    """
    Retrieves an LLM client, prioritizing DeepSeek, then Groq, then OpenAI.
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

    # 3. OpenAI (Fallback)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and "your_" not in openai_api_key.lower():
        try:
            print("Attempting to initialize OpenAI client.")
            client = openai.OpenAI(api_key=openai_api_key)
            print("OpenAI client initialized successfully.")
            return {"type": "openai", "client": client, "model": "gpt-4o"}
        except Exception as e:
            print(f"OpenAI client initialization failed: {e}.")

    raise ValueError("No valid LLM client could be initialized. Please check your DEEPSEEK_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY.")
