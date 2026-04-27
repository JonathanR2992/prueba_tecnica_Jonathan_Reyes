import json
import os
import re

from app.config import settings


class TextCleaner:
    def clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def clean(self):
        input_path = os.path.join(settings.raw_data_path, "scraped_pages.json")
        output_path = os.path.join(settings.clean_data_path, "clean_pages.json")

        os.makedirs(settings.clean_data_path, exist_ok=True)

        with open(input_path, "r", encoding="utf-8") as file:
            pages = json.load(file)

        clean_pages = []

        for page in pages:
            text = self.clean_text(page.get("text", ""))

            if len(text) > 200:
                clean_pages.append({
                    "url": page.get("url", ""),
                    "title": page.get("title", ""),
                    "text": text,
                })

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(clean_pages, file, ensure_ascii=False, indent=2)

        return output_path, len(clean_pages)


if __name__ == "__main__":
    cleaner = TextCleaner()
    output_path, total = cleaner.clean()

    print(f"Páginas limpias: {total}")
    print(f"Archivo guardado en: {output_path}")