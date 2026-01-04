from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # N8N Configuration
    N8N_BASE_URL: str = "http://localhost:5678"
    N8N_TIMEOUT: int = 30
    N8N_MAX_RETRIES: int = 3
    
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "ai_education_platform"
    
    # Application Configuration
    APP_NAME: str = "AI Education Platform Backend"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # LLM Configuration (Add these fields to match .env file)
    OPENAI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    SECONDARY_GEMINI_KEY: str | None = None
    THIRD_GEMINI_KEY: str | None = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
