from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RAG Bank Assistant"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    target_base_url: str = "https://www.bbva.com.co/"
    max_pages: int = 30
    request_timeout: int = 10
    user_agent: str = "Mozilla/5.0 (compatible; RAGBankAssistant/1.0)"

    chunk_size: int = 900
    chunk_overlap: int = 150
    top_k: int = 5
    use_reranker: bool = True
    conversation_window_n: int = 6

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.2:3b"

    raw_data_dir: str = "data/raw"
    clean_data_dir: str = "data/clean"
    chroma_dir: str = "chroma_data"
    sqlite_db_path: str = "data/conversations.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
