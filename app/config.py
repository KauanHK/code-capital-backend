from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_TITLE: str = "SW Backend API"
    API_VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/sw"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
