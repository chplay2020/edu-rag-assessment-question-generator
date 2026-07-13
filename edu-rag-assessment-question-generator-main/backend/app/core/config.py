from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Edu RAG Assessment Question Generator"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"] # Mặc định cho phép tất cả trong môi trường dev
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
