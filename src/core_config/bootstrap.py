from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, JsonConfigSettingsSource
from .static_values import ENV_PREFIX
from loguru import logger
from core_config.root_path import PROJECT_ROOT

class BootstrapConfig(BaseSettings):
    # Definition der Dateinamen ohne Pfad
    # Der Wert muss in config.json oder Env stehen
    env_file: str | None = None
    api_config:str | None = None
    api_selection:str | None = None
    env_prefix: str = ENV_PREFIX
    json_file_path: Path = PROJECT_ROOT / "configs" / "config.json"
    model_config = SettingsConfigDict(
        # Pydantic liest config.json
        json_file = json_file_path,
        extra="ignore"
    )
    # Diese Methode ist notwendig, damit Pydantic die json_file auch wirklich liest  
    @classmethod  
    def settings_customise_sources(  
        cls,  
        settings_cls: type[BaseSettings],  
        init_settings: PydanticBaseSettingsSource,  
        env_settings: PydanticBaseSettingsSource,  
        dotenv_settings: PydanticBaseSettingsSource,  
        file_secret_settings: PydanticBaseSettingsSource,  
    ) -> tuple[PydanticBaseSettingsSource, ...]:  
        return (  
            init_settings,  # 1. Werte vom Konstruktor
            JsonConfigSettingsSource(settings_cls), # config.json
            dotenv_settings, # .env-Datei
            env_settings  # 4. System-Umgebungsvariablen
        )

try:
    bootstrap = BootstrapConfig()
    logger.debug(f"Bootstrap json_file path: {BootstrapConfig.model_config.get('json_file')}")
except Exception as e:
    raise RuntimeError(f"Kritischer Konfigurationsfehler: {e}")