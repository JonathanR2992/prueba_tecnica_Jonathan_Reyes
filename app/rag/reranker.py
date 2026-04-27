from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TfidfReranker:
    """Reranker simple y gratuito. Reordena resultados por similitud TF-IDF contra la pregunta."""

    def rerank(self, query: str, documents: list[dict], top_k: int) -> list[dict]:
        if not documents:
            return []
        corpus = [query] + [doc["text"] for doc in documents]
        vectorizer = TfidfVectorizer().fit_transform(corpus)
        scores = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()

        ranked = []
        for doc, score in zip(documents, scores):
            doc = dict(doc)
            doc["rerank_score"] = float(score)
            ranked.append(doc)
        return sorted(ranked, key=lambda item: item["rerank_score"], reverse=True)[:top_k]
