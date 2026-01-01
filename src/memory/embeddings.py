from langchain_ollama import OllamaEmbeddings
from ..config import EMBEDDING_MODEL

model = None

def get_model():
    global model
    if model is None:
        print("Loading embedding model... (this may take a moment on first run)")
        model = OllamaEmbeddings(model=EMBEDDING_MODEL)
    return model

def embed_text(text):
    return get_model().embed_query([text])[0]