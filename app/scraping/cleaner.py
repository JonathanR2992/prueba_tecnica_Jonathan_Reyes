import json
import os
import re
from dataclasses import dataclass

from app.config import settings


@dataclass
class CleanDocument:
    id: str
    url: str
    title: str
    text: str


class TextCleaner:
    def clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\sáéíóúÁÉÍÓÚñÑüÜ.,;:¿?¡!%$()/-]", " ", text)
        return text.strip()

    def clean_file(self, input_path: str) -> list[CleanDocument]:
        with open(input_path, "r", encoding="utf-8") as file:
            raw_pages = json.load(file)

        documents = []
        for index, page in enumerate(raw_pages):
            clean_text = self.clean_text(page.get("text", ""))
            if len(clean_text) < 200:
                continue
            documents.append(
                CleanDocument(
                    id=f"doc_{index}",
                    url=page.get("url", ""),
                    title=page.get("title", ""),
                    text=clean_text,
                )
            )
        return documents

    def save_clean(self, documents: list[CleanDocument]) -> str:
        os.makedirs(settings.clean_data_dir, exist_ok=True)
        output_path = os.path.join(settings.clean_data_dir, "clean_documents.json")
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump([doc.__dict__ for doc in documents], file, ensure_ascii=False, indent=2)
        return output_path
