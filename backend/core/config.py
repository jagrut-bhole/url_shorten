from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "URL Shortener"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:2040@localhost:5432/url_shortener"
    
    # JWT
    SECRET_KEY: str = "jagrutbhole2004"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15        # short-lived
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7           # long-lived
    
    # App base URL
    BASE_URL: str = "http://localhost:8000"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
        
# Single instance — import this everywhere
settings = Settings()