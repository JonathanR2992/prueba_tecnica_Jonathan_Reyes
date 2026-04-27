from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.analytics.metrics import ConversationAnalytics
from app.patterns.facade import RAGService
from app.rag.vector_store import ChromaVectorStore
from app.scraping.cleaner import TextCleaner
from app.scraping.scraper import BankWebsiteScraper

router = APIRouter()
rag_service = RAGService()


class AskRequest(BaseModel):
    conversation_id: str = Field(..., examples=["session_001"])
    question: str = Field(..., examples=["¿Qué productos de ahorro ofrece el banco?"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/ingest")
def ingest():
    try:
        scraper = BankWebsiteScraper()
        pages = scraper.scrape()
        raw_path = scraper.save_raw(pages)

        cleaner = TextCleaner()
        documents = cleaner.clean_file(raw_path)
        clean_path = cleaner.save_clean(documents)

        vector_store = ChromaVectorStore()
        indexed_chunks = vector_store.index_clean_documents(clean_path)

        return {
            "scraped_pages": len(pages),
            "clean_documents": len(documents),
            "indexed_chunks": indexed_chunks,
            "raw_path": raw_path,
            "clean_path": clean_path,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/ask")
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
    return rag_service.ask(request.conversation_id, request.question)


@router.get("/analytics")
def analytics():
    return ConversationAnalytics().summary()
