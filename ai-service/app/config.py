from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    port: int = 8000
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    ai_service_internal_key: str = ""
    kb_path: Path = BASE_DIR / "data" / "hidji_knowledge_base.json"
    forecast_bundle_path: Path = BASE_DIR / "app" / "ml_forecast" / "hidji_ridge_bundle_v1.joblib"
    forecast_master_path: Path = BASE_DIR / "app" / "ml_forecast" / "master_bahan_ref.json"
    intent_model_version: str = "rule-baseline-v0.1"
    llm_timeout_seconds: float = 8.0

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_llm_configured(self) -> bool:
        key = self.gemini_api_key.strip()
        return bool(key) and key != "your_gemini_api_key_here"


settings = Settings()
