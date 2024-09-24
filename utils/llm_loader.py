from llama_index.llms.ollama import Ollama


def load_ollama_model(model_name: str):
    llm_instance = Ollama(model=model_name, temperature=0, request_timeout=60)
    return llm_instance
