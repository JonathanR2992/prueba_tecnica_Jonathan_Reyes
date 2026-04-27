from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RAG Bank Assistant"
    environment: str = "development"

    target_base_url: str = "https://www.bbva.com.co/"
    user_agent: str = "Mozilla/5.0"
    max_pages: int = 20
    request_timeout: int = 15

    raw_data_path: str = "data/raw"
    clean_data_path: str = "data/clean"
    chroma_path: str = "data/chroma"
    sqlite_path: str = "data/conversations.db"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    collection_name: str = "bank_documents"

    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k: int = 5
    memory_window: int = 5
    use_reranker: bool = False

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()