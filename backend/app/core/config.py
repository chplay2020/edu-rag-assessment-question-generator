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

    # Embeddings
    EMBEDDING_PROVIDER: str = "fake"
    EMBEDDING_MODEL: str = "fake-deterministic-embedding"
    EMBEDDING_DIMENSION: int = 768

    # LLM
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.5-flash"
    GEMINI_API_KEY: str | None = None
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
