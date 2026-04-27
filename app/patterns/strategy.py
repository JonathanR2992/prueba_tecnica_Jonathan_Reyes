from abc import ABC, abstractmethod

from app.rag.reranker import TfidfReranker


class RetrievalStrategy(ABC):
    """Strategy: permite cambiar la política de recuperación sin afectar el servicio RAG."""

    @abstractmethod
    def retrieve(self, query: str, vector_store, top_k: int) -> list[dict]:
        raise NotImplementedError


class BasicRetrievalStrategy(RetrievalStrategy):
    def retrieve(self, query: str, vector_store, top_k: int) -> list[dict]:
        return vector_store.search(query, top_k)


class RerankedRetrievalStrategy(RetrievalStrategy):
    def __init__(self):
        self.reranker = TfidfReranker()

    def retrieve(self, query: str, vector_store, top_k: int) -> list[dict]:
        candidates = vector_store.search(query, top_k=max(top_k * 2, 10))
        return self.reranker.rerank(query, candidates, top_k)
