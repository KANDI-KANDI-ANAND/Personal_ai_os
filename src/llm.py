from langchain_ollama import ChatOllama
from .config import MODEL_NAME, LLM_TEMPERATURE

def get_llm():
    """
    Return a ChatOllama instance connected to local Ollama server.
    """
    return ChatOllama(model=MODEL_NAME,
     temperature=LLM_TEMPERATURE,
     top_p=0.9,
     num_ctx=2048
     )