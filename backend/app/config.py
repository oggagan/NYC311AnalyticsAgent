from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    data_path: str = "./data/dataset.csv"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    llm_model: str = "deepseek-chat"
    llm_temperature: float = 0.0
    llm_timeout: int = 60
    max_retries: int = 3
    sql_timeout: int = 30

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
