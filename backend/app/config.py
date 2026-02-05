from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve .env relative to the backend/ directory
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    openai_api_key: str = ""
    ncbi_api_key: str = ""
    openalex_api_key: str = ""
    frontend_url: str = "http://localhost:3000"
    log_level: str = "INFO"

    model_config = {
        "env_file": str(_ENV_FILE) if _ENV_FILE.exists() else None,
        "env_file_encoding": "utf-8",
    }


settings = Settings()
