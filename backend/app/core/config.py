from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Edu RAG Assessment Question Generator"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "supersecretkey-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"] # Mặc định cho phép tất cả trong môi trường dev
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "edu_rag_db"

    # Vector store
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_MATERIAL_COLLECTION: str = "material_chunks"
    QDRANT_QUESTION_COLLECTION: str = "question_vectors"
    QDRANT_TIMEOUT_SECONDS: int = 30

    # Embeddings: "gemini" (production) hoặc "fake" (deterministic, dùng cho test/offline)
    EMBEDDING_PROVIDER: str = "fake"
    EMBEDDING_MODEL: str = "fake-deterministic-embedding"
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_BATCH_SIZE: int = 32
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"

    # LLM (Gemini API)
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.5-flash"
    GEMINI_API_KEY: str | None = None
    LLM_TEMPERATURE: float = 0.4
    LLM_MAX_OUTPUT_TOKENS: int = 8192
    LLM_TIMEOUT_SECONDS: int = 120
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_BASE_DELAY: float = 2.0
    # 0 = tắt thinking (nhanh/rẻ), -1 = để Gemini tự quyết định
    LLM_THINKING_BUDGET: int = 0
    # Cho phép rơi về FakeLLMProvider khi thiếu GEMINI_API_KEY (bật cho dev/test)
    LLM_ALLOW_FAKE_FALLBACK: bool = True

    # RAG retrieval
    RAG_TOP_K: int = 8
    RAG_QUERY_EXPANSION: bool = True
    RAG_MAX_CONTEXT_CHARS: int = 24_000
    RAG_MIN_SCORE: float = 0.0

    # Question generation pipeline
    GENERATION_MAX_ATTEMPTS: int = 3
    DUPLICATE_THRESHOLD: float = 0.92
    NEAR_DUPLICATE_TEXT_RATIO: float = 0.9
    ENABLE_LLM_JUDGE: bool = False
    LLM_JUDGE_MIN_SCORE: float = 0.6


    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
