from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_TITLE: str = "SW Backend API"
    API_VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/sw"
    JWT_SECRET_KEY: str = "change-me-in-production-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
