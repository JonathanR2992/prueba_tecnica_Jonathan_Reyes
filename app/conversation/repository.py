import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings


class ConversationRepository:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.sqlite_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_message(self, conversation_id: str, user_message: str, assistant_message: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO conversations(conversation_id, user_message, assistant_message, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, user_message, assistant_message, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()

    def get_recent_history(self, conversation_id: str, limit: int) -> list[dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT user_message, assistant_message, created_at
                FROM conversations
                WHERE conversation_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (conversation_id, limit),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def get_all(self) -> list[dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM conversations ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]
