from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./database.db"
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
