from pydantic_settings import BaseSettings, SettingsConfigDict
from .custom_dataclasses import PATHS
import os

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PATHS.ENV_FILE) if PATHS.ENV_FILE else None,
        extra="allow" # für dynamische Variablen
    )

    def get_var(self, key: str) -> str | None:
        """Sucht erst in .env.*, dann im System-Env."""
        val:str|None = (self.model_extra or {}).get(key)
        if val is None:
            return str(val)
        return os.getenv(key)

# Singleton
settings = AppSettings()