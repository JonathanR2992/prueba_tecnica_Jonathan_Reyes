from collections import Counter

import pandas as pd

from app.conversation.repository import ConversationRepository


class ConversationAnalytics:
    def __init__(self):
        self.repository = ConversationRepository()

    def summary(self) -> dict:
        rows = self.repository.get_all()
        if not rows:
            return {
                "total_messages": 0,
                "total_conversations": 0,
                "avg_user_message_length": 0,
                "top_terms": [],
            }

        df = pd.DataFrame(rows)
        all_text = " ".join(df["user_message"].astype(str).str.lower())
        words = [word for word in all_text.split() if len(word) > 4]
        top_terms = Counter(words).most_common(10)

        return {
            "total_messages": int(len(df)),
            "total_conversations": int(df["conversation_id"].nunique()),
            "avg_user_message_length": float(df["user_message"].str.len().mean()),
            "top_terms": top_terms,
        }
