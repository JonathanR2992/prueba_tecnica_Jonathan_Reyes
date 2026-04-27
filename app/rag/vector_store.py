import json
from pathlib import Path
import hashlib

import chromadb

from app.config import settings
from app.rag.chunking import TextChunker
from app.rag.embeddings import EmbeddingModel


class ChromaVectorStore:
    def __init__(self, collection_name: str = "bank_site_documents"):
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedder = EmbeddingModel()
        self.chunker = TextChunker()

    def index_clean_documents(self, clean_path: str | None = None) -> int:
        clean_path = clean_path or f"{settings.clean_data_path}/clean_pages.json"
        path = Path(clean_path)

        if not path.exists():
            raise FileNotFoundError(f"No existe el archivo limpio: {clean_path}")

        documents = json.loads(path.read_text(encoding="utf-8"))
        ids, texts, metadatas = [], [], []

        for doc_idx, doc in enumerate(documents):
            text = doc.get("text", "")
            url = doc.get("url", "")
            title = doc.get("title", "")

            chunks = self.chunker.split(text)

            for chunk_idx, chunk in enumerate(chunks):
                stable_id = hashlib.md5(
                    f"{url}_{doc_idx}_{chunk_idx}".encode("utf-8")
                ).hexdigest()

                ids.append(stable_id)
                texts.append(chunk)
                metadatas.append(
                    {
                        "url": url,
                        "title": title,
                        "doc_id": str(doc_idx),
                    }
                )

        if not texts:
            print("No se encontraron textos para indexar.")
            return 0

        embeddings = self.embedder.embed(texts)

        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        print(f"Chunks indexados: {len(texts)}")
        return len(texts)

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        top_k = top_k or settings.top_k
        query_embedding = self.embedder.embed([query])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        output = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i, doc in enumerate(documents):
            output.append(
                {
                    "text": doc,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "distance": distances[i] if i < len(distances) else None,
                }
            )

        return output


if __name__ == "__main__":
    vector_store = ChromaVectorStore()
    total = vector_store.index_clean_documents()
    print(f"Total de chunks indexados: {total}")