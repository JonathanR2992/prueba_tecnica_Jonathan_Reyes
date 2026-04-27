from app.config import settings
from app.conversation.memory import ConversationMemory
from app.patterns.factory import ComponentFactory
from app.patterns.strategy import BasicRetrievalStrategy, RerankedRetrievalStrategy


class RAGService:
    """Facade: expone una interfaz simple para ejecutar el flujo completo del sistema RAG."""

    def __init__(self):
        self.vector_store = ComponentFactory.create_vector_store()
        self.generator = ComponentFactory.create_generator(settings.llm_provider)
        self.memory = ConversationMemory()
        self.retrieval_strategy = (
            RerankedRetrievalStrategy()
            if settings.use_reranker
            else BasicRetrievalStrategy()
        )

    def ask(self, conversation_id: str, question: str):
        try:
            clean_question = question.strip()

            if not clean_question:
                return {
                    "conversation_id": conversation_id,
                    "answer": "La pregunta no puede estar vacía.",
                    "sources": [],
                }

            history = self.memory.load(conversation_id)

            retrieved_docs = self.retrieval_strategy.retrieve(
                clean_question,
                self.vector_store,
                settings.top_k,
            )

            answer = self.generator.generate(
                question=clean_question,
                context=retrieved_docs,
                history=history,
            )

            self.memory.save(conversation_id, clean_question, answer)

            return {
                "conversation_id": conversation_id,
                "answer": answer,
                "sources": retrieved_docs,
            }

        except Exception as error:
            return {
                "conversation_id": conversation_id,
                "answer": "Ocurrió un error procesando la pregunta. Revisa los logs del sistema.",
                "sources": [],
                "error": str(error),
            }