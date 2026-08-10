from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://chessflow_user:chessflow_password@db:5432/chessflow_db"

    REDIS_URL: str = "redis://redis:6379"

    SECRET_KEY: str = "chessflow-secret-key-change-in-production-min-32-chars-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    STOCKFISH_PATH: str = "/usr/games/stockfish"
    DEFAULT_ANALYSIS_DEPTH: int = 20
    ANALYSIS_TIMEOUT: int = 30

    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()