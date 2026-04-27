from app.config import settings
from app.conversation.repository import ConversationRepository


class ConversationMemory:
    def __init__(self):
        self.repository = ConversationRepository()

    def load(self, conversation_id: str) -> list[dict]:
        return self.repository.get_recent_history(conversation_id, settings.conversation_window_n)

    def save(self, conversation_id: str, question: str, answer: str) -> None:
        self.repository.save_message(conversation_id, question, answer)
