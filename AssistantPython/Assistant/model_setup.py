import os
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm


def get_model():
    load_dotenv()
    MODEL_SOURCE = os.getenv("MODEL_SOURCE", "local")
    if MODEL_SOURCE == "local":
        LOCAL_MODEL = os.getenv("LOCAL_MODEL", "mistral")
        return LiteLlm(f'ollama_chat/{LOCAL_MODEL}')
    elif MODEL_SOURCE == "openai":
        OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        OPENAI_KEY = os.getenv("OPENAI_API_KEY")
        return LiteLlm(f'openai/{OPENAI_MODEL}')
    elif MODEL_SOURCE == "google":
        GEMINI_MODEL = os.getenv("GEMINI_MODEL")
        GEMINI_KEY = os.getenv("GEMINI_API_KEY")
        return LiteLlm(f'google/{GEMINI_MODEL}')
    return None
