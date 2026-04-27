from app.rag.generator import OllamaGenerator
from app.rag.vector_store import ChromaVectorStore


class ComponentFactory:
    """Factory Method: centraliza la creación de componentes intercambiables."""

    @staticmethod
    def create_vector_store():
        return ChromaVectorStore()

    @staticmethod
    def create_generator(provider: str = "ollama"):
        if provider != "ollama":
            raise ValueError(f"Proveedor LLM no soportado: {provider}")
        return OllamaGenerator()
