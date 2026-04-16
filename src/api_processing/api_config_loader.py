from typing import cast, Any
from re import Match
import yaml
import os
from pathlib import Path
from loguru import logger

from core_config import PATHS
from core_config.custom_dataclasses import ApiConfigKeys, HeaderKeys, RegexPatterns
from core_config.custom_types import ApiConfig
from core_config import bootstrap


class ApiConfigLoader:
    """Kapselt die Logik zum Laden und Auflösen von API-Konfigurationen."""

    def __init__(self, path: Path = PATHS.API_CONFIG):
        self.path = path
        self._raw_configs: list[dict[str,Any]] = self._load_yaml()
        self.env_prefix: str = bootstrap.env_prefix

    def _load_yaml(self) -> list[dict[str,Any]]:
        if not self.path.exists():
            raise FileNotFoundError(f"YAML config not found at {self.path}")
        with self.path.open() as f:
            return yaml.safe_load(f) or []

    # --- Öffentliche Methoden ---

    def get_configs(self, keys: list[str]) -> list[ApiConfig]:
        """Lädt Daten-Configs: name, endpoint, headers, filename sind Pflicht."""
        out = [
            self._process_entry(conf)
            for conf in self._raw_configs
            if conf.get(ApiConfigKeys.NAME) in keys
        ]
        if not out:
            raise RuntimeError(f"No configs found for keys: {keys}")
        return out

    def get_single(self, name: str) -> ApiConfig:
        """Lädt eine einzelne Daten-Config."""
        return self.get_configs([name])[0]

    def get_token_config(self, name: str) -> ApiConfig:
        """
        Lädt eine Token-Config.
        Pflichtfelder: name, endpoint, headers.
        Kein filename erforderlich, da kein Download stattfindet.
        """
        for conf in self._raw_configs:
            if conf.get(ApiConfigKeys.NAME) == name:
                resolved: dict[str,Any] = self._resolve_variables(conf)
                return self._validate_token(resolved)
        raise RuntimeError(f"Token config '{name}' not found in YAML.")

    # --- Interne Pipeline ---

    def _process_entry(self, entry: dict[str,Any]) -> ApiConfig:
        resolved  = self._resolve_variables(entry)
        return self._validate(resolved)

    def _resolve_variables(self, entry: dict[str,Any]) -> dict[str,Any]:
        resolved = entry.copy()
        for key in ApiConfigKeys.ENV_RESOLVABLE_FIELDS:
            value = resolved.get(key)
            if isinstance(value, str):
                resolved[key] = self._replace_env_var(value)
        if ApiConfigKeys.HEADERS in resolved:
            resolved[ApiConfigKeys.HEADERS] = self._resolve_auth_headers(
                resolved[ApiConfigKeys.HEADERS]
            )
        return resolved

    def _replace_env_var(self, text: str) -> str:
        prefix:str = self.env_prefix
        def repl(match: Match[str]) -> str:
            var: str = match.group(1)
            val: str | None = os.getenv(f"{prefix}{var}") or os.getenv(var)
            if val is None:
                raise RuntimeError(f"Required environment variable '{prefix}{var}' or '{var}' is not set.")
            return val
        return RegexPatterns.ENV_VAR.sub(repl, text)

    
    def _resolve_auth_headers(self, headers: dict[str, str]) -> dict[str, str | None]:
        new_headers: dict[str,str|None] = dict(headers)
        if HeaderKeys.AUTH_ENV in new_headers:
            env_key:str|None = new_headers.pop(HeaderKeys.AUTH_ENV)
            if env_key is None:
                logger.error("No environment key provided for auth.")
                return new_headers
            token = os.getenv(env_key)
            if not token:
                logger.error(f"Token variable '{env_key}' is empty or missing!")
                new_headers[HeaderKeys.AUTH] = None
            else:
                new_headers[HeaderKeys.AUTH] = f"Bearer {token}"
        return new_headers

    def _validate(self, entry: dict[str,Any]) -> ApiConfig:
        """Validierung für Daten-Configs: filename ist Pflicht."""
        required = {
            ApiConfigKeys.NAME,
            ApiConfigKeys.ENDPOINT,
            ApiConfigKeys.HEADERS,
            ApiConfigKeys.FILENAME,  # Pflicht für Download-Einträge
        }
        missing = required - entry.keys()
        if missing:
            raise ValueError(
                f"Entry '{entry.get(ApiConfigKeys.NAME, '?')}' missing keys: {missing}"
            )
        return cast(ApiConfig, entry)

    def _validate_token(self, entry: dict[str,Any]) -> ApiConfig:
        """Validierung für Token-Configs: kein filename erforderlich."""
        required = {
            ApiConfigKeys.NAME,
            ApiConfigKeys.ENDPOINT,
            ApiConfigKeys.HEADERS,
        }
        missing = required - entry.keys()
        if missing:
            raise ValueError(
                f"Token entry '{entry.get(ApiConfigKeys.NAME, '?')}' missing keys: {missing}"
            )
        return cast(ApiConfig, entry)


# --- Fassade ---

def get_api_configs(keys: list[str]) -> list[ApiConfig]:
    return ApiConfigLoader().get_configs(keys)

def get_single_config(name: str) -> ApiConfig:
    return ApiConfigLoader().get_single(name)