import os
import logging
import openai

# Set up logging (this will appear in Render logs)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

try:
    from groq import Groq
    HAS_GROQ_PACKAGE = True
except ImportError:
    HAS_GROQ_PACKAGE = False

def get_all_llm_clients():
    """
    Returns a list of all available LLM configurations based on environment variables.
    Each config is a dictionary: {'type': str, 'client': object, 'model': str}
    """
    clients = []

    # Safe logging of key presence
    deepseek_key_exists = os.environ.get("DEEPSEEK_API_KEY") is not None
    groq_key_exists = os.environ.get("GROQ_API_KEY") is not None
    openai_key_exists = os.environ.get("OPENAI_API_KEY") is not None
    google_key_exists = (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")) is not None

    logger.info(f"🔍 DEEPSEEK_API_KEY present: {deepseek_key_exists}")
    logger.info(f"🔍 GROQ_API_KEY present: {groq_key_exists}")
    logger.info(f"🔍 OPENAI_API_KEY present: {openai_key_exists}")
    logger.info(f"🔍 GOOGLE_API_KEY/GEMINI_API_KEY present: {google_key_exists}")

    # Check for variables with slightly different names
    alt_keys = {
        "DEEPSEEK_KEY": os.environ.get("DEEPSEEK_KEY") is not None,
        "GROQ_KEY": os.environ.get("GROQ_KEY") is not None,
        "OPENAI_KEY": os.environ.get("OPENAI_KEY") is not None,
        "GOOGLE_KEY": os.environ.get("GOOGLE_KEY") is not None
    }
    for alt_name, exists in alt_keys.items():
        if exists:
            logger.warning(f"⚠️ Found alternative key name: {alt_name}. The app currently expects *_API_KEY.")

    # 1. DeepSeek
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_api_key and "your_" not in deepseek_api_key.lower():
        try:
            client = openai.OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
            clients.append({"type": "deepseek", "client": client, "model": "deepseek-chat"})
            logger.info("✅ DeepSeek client initialized successfully.")
        except Exception as e:
            logger.error(f"❌ DeepSeek initialization failed: {e}")

    # 2. Groq
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and "your_" not in groq_api_key.lower():
        try:
            if HAS_GROQ_PACKAGE:
                client = Groq(api_key=groq_api_key)
                logger.info("✅ Groq client initialized using native package.")
            else:
                client = openai.OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
                logger.info("✅ Groq client initialized using OpenAI compatibility layer.")
            clients.append({"type": "groq", "client": client, "model": "llama-3.3-70b-versatile"})
        except Exception as e:
            logger.error(f"❌ Groq initialization failed: {e}")

    # 3. OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and "your_" not in openai_api_key.lower():
        try:
            client = openai.OpenAI(api_key=openai_api_key)
            clients.append({"type": "openai", "client": client, "model": "gpt-4o"})
            logger.info("✅ OpenAI client initialized successfully.")
        except Exception as e:
            logger.error(f"❌ OpenAI initialization failed: {e}")

    # 4. Google Gemini
    google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if google_api_key and "your_" not in google_api_key.lower() and HAS_GENAI:
        try:
            client = genai.Client(api_key=google_api_key)
            clients.append({"type": "gemini", "client": client, "model": "gemini-1.5-flash"})
            logger.info("✅ Google Gemini client initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")

    if not clients:
        logger.error("❌ No valid LLM clients could be initialized. Please check your API keys in Render.")

    return clients

def get_llm_client():
    """
    Retrieves the primary LLM client. Included for backward compatibility.
    """
    clients = get_all_llm_clients()
    if not clients:
        raise ValueError("No valid LLM client could be initialized. Please check your API keys.")
    return clients[0]
