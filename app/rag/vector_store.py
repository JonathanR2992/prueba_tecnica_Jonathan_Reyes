import json
from pathlib import Path

import chromadb

from app.config import settings
from app.rag.chunking import TextChunker
from app.rag.embeddings import EmbeddingModel


class ChromaVectorStore:
    def __init__(self, collection_name: str = "bank_site_documents"):
        self.client = chromadb.PersistentClient(path=settings.chroma_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedder = EmbeddingModel()
        self.chunker = TextChunker()

    def index_clean_documents(self, clean_path: str | None = None) -> int:
        clean_path = clean_path or f"{settings.clean_data_dir}/clean_documents.json"
        path = Path(clean_path)
        if not path.exists():
            raise FileNotFoundError(f"No existe el archivo limpio: {clean_path}")

        documents = json.loads(path.read_text(encoding="utf-8"))
        ids, texts, metadatas = [], [], []

        for doc in documents:
            chunks = self.chunker.split(doc["text"])
            for idx, chunk in enumerate(chunks):
                ids.append(f"{doc['id']}_chunk_{idx}")
                texts.append(chunk)
                metadatas.append({"url": doc["url"], "title": doc["title"], "doc_id": doc["id"]})

        if not texts:
            return 0

        embeddings = self.embedder.embed(texts)
        self.collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
        return len(texts)

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        top_k = top_k or settings.top_k
        query_embedding = self.embedder.embed([query])[0]
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

        output = []
        for i, doc in enumerate(results.get("documents", [[]])[0]):
            output.append({
                "text": doc,
                "metadata": results.get("metadatas", [[]])[0][i],
                "distance": results.get("distances", [[]])[0][i],
            })
        return output
