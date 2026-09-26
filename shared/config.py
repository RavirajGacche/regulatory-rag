from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["local", "staging", "prod"] = "local"
    debug: bool = False

    pg_user: str = "rag"
    pg_password: SecretStr
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_db: str = "rag"

    mongo_user: str = "rag"
    mongo_password: SecretStr
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "rag"

    redis_host: str = "localhost"
    redis_port: int = 6379

    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    llm_provider: str = "groq"
    groq_api_key: SecretStr
    groq_model: str = "openai/gpt-oss-120b"
    groq_small_model: str = "openai/gpt-oss-20b"

    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 7

    @property
    def postgres_url(self) -> str:
        pwd = quote_plus(self.pg_password.get_secret_value())
        return f"postgresql+psycopg://{self.pg_user}:{pwd}@{self.pg_host}:{self.pg_port}/{self.pg_db}"

    @property
    def mongo_url(self) -> str:
        pwd = quote_plus(self.mongo_password.get_secret_value())
        return f"mongodb://{self.mongo_user}:{pwd}@{self.mongo_host}:{self.mongo_port}/?authSource=admin"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
