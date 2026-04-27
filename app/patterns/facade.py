from app.config import settings
from app.conversation.memory import ConversationMemory
from app.patterns.factory import ComponentFactory
from app.patterns.strategy import BasicRetrievalStrategy, RerankedRetrievalStrategy


class RAGService:
    """Facade: expone una interfaz simple para preguntar al sistema RAG."""

    def __init__(self):
        self.vector_store = ComponentFactory.create_vector_store()
        self.generator = ComponentFactory.create_generator(settings.llm_provider)
        self.memory = ConversationMemory()
        self.retrieval_strategy = RerankedRetrievalStrategy() if settings.use_reranker else BasicRetrievalStrategy()

    def ask(self, conversation_id: str, question: str) -> dict:
        history = self.memory.load(conversation_id)
        docs = self.retrieval_strategy.retrieve(question, self.vector_store, settings.top_k)
        context = "\n\n".join([f"Fuente: {d['metadata'].get('url')}\n{d['text']}" for d in docs])
        answer = self.generator.generate(question=question, context=context, history=history)
        self.memory.save(conversation_id, question, answer)
        return {
            "conversation_id": conversation_id,
            "question": question,
            "answer": answer,
            "sources": [doc["metadata"] for doc in docs],
        }
