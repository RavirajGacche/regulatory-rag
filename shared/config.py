from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "local"
    debug: bool = True

    pg_user: str = "rag"
    pg_password: str = "ragpass"
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_db: str = "rag"

    mongo_user: str = "rag"
    mongo_password: str = "ragpass"
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "rag"

    redis_host: str = "localhost"
    redis_port: int = 6379

    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    llm_provider: str = "groq"
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 7

    @property
    def postgres_url(self) -> str:
        return (f"postgresql+psycopg://{self.pg_user}:{self.pg_password}"
                f"@{self.pg_host}:{self.pg_port}/{self.pg_db}")

    @property
    def mongo_url(self) -> str:
        return (f"mongodb://{self.mongo_user}:{self.mongo_password}"
                f"@{self.mongo_host}:{self.mongo_port}/?authSource=admin")

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
