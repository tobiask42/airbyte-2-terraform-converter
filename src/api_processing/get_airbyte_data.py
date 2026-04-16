from pathlib import Path
from collections import defaultdict
from loguru import logger
import httpx
import json
from typing import Any
from collections.abc import Mapping
from core_config import PATHS
from core_config.custom_dataclasses import ApiConfigKeys, HeaderKeys
import core_config.static_values as constants
from core_config.custom_types import ApiConfig
from api_processing.api_config_loader import ApiConfigLoader
from .get_bearer_token import get_airbyte_token
from utils.airbyte_utils import merge_next_with_base


def load_api_selection() -> tuple[dict[str, str], list[str]]:
    """Lädt die API-Selektion und gibt tokens_map und datakeys zurück."""
    with PATHS.API_SELECTION.open() as f:
        api_info = json.load(f)
    tokens_map: dict[str, str] = api_info[constants.API_SELECTION_TOKENSKEY]
    datakeys: list[str] = api_info[constants.API_SELECTION_DATAKEY]
    return tokens_map, datakeys


def group_keys(
    tokens_map: dict[str, str], datakeys: list[str]
) -> tuple[defaultdict[str, list[str]], list[str]]:
    """Gruppiert datakeys in 'mit Auth' und 'ohne Auth'."""
    withauth: defaultdict[str, list[str]] = defaultdict(list)
    noauth: list[str] = []

    for datakey in datakeys:
        matched = any(datakey.startswith(prefix) for prefix in tokens_map)
        if matched:
            for prefix in tokens_map:
                if datakey.startswith(prefix):
                    withauth[prefix].append(datakey)
        else:
            noauth.append(datakey)

    return withauth, noauth


def prepare_output_dirs(timestamp: str) -> tuple[Path, Path]:
    """Erstellt die Ausgabeordner falls nötig und gibt die Pfade zurück."""
    base_data = PATHS.DATA_DIR
    data_dir = base_data / f"{constants.DATA_PREFIX}{timestamp}"

    base_data.mkdir(exist_ok=True)
    logger.info(
        "Base data folder doesn't exist and is created."
        if not base_data.exists()
        else "Base data folder exists and is used."
    )

    data_dir.mkdir(exist_ok=True)
    logger.info(f"Data folder at {data_dir.resolve()}")

    return base_data, data_dir


def _fetch_paginated(endpoint: str, headers: Mapping[str,str], conf: ApiConfig) -> dict[str,Any]:
    """Führt einen paginierten GET-Request durch und gibt alle Ergebnisse zurück."""
    results:list[str] = []
    
    # Sicherer Zugriff mit .get() und Default-Werten
    items_key = conf.get(ApiConfigKeys.ITEMS_KEY, "data")  # Default "data" falls nicht in YAML
    next_key = conf.get(ApiConfigKeys.NEXT_KEY, "next")    # Default "next" falls nicht in YAML
    
    next_url: str | None = endpoint

    while next_url:
        try:
            response = httpx.get(next_url, headers=headers)
            logger.info(f"Request Endpoint: {next_url}")
            logger.info(f"Response Status: {response.status_code}")
            response.raise_for_status()

            data = response.json()

            # Prüfung ob der items_key im JSON-Response existiert
            if items_key not in data:
                logger.error(f"Key '{items_key}' not found in response. Structure might have changed.")
                break

            results.extend(data[items_key])
            
            # Nächste URL aus dem Response holen
            raw_next = data.get(next_key)
            next_url = merge_next_with_base(raw_next, endpoint) if raw_next else None

            if next_url:
                logger.info(f"Next page URL: {next_url}")

        except Exception as e:
            logger.error(f"Error in API request: {e}")
            break

    return {constants.API_DATAKEY: results}


def _dump_json(path: Path, data: dict[str,Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)



def _download_single(conf: ApiConfig, timestamp: str, output_dir: Path) -> None:
    filename = f"{conf[ApiConfigKeys.FILENAME]}_{timestamp}.json"
    logger.info(f"--- Starting download: {conf[ApiConfigKeys.NAME]} ---")
    logger.info(f"  Endpoint: {conf[ApiConfigKeys.ENDPOINT]}")
    logger.info(f"  Filename: {filename}")

    raw_headers = conf[ApiConfigKeys.HEADERS]
    request_headers: dict[str, str] = {
        k: v for k, v in raw_headers.items()
        if isinstance(v, str)
    }

    data = _fetch_paginated(
        conf[ApiConfigKeys.ENDPOINT],
        request_headers,
        conf,
    )
    _dump_json(output_dir / filename, data)
    logger.success(f"Stored file under {filename}")


def download_with_auth(
    prefix: str,
    datakeys: list[str],
    tokens_map: dict[str, str],
    loader: ApiConfigLoader,
    timestamp: str,
    output_dir: Path,
) -> None:
    """Holt ein Bearer-Token und lädt alle zugehörigen Daten herunter."""
    token_conf_name = tokens_map[prefix]
    logger.info(f"Fetching token for {prefix}: {token_conf_name}")

    token_conf = loader.get_token_config(token_conf_name)
    bearer_token = get_airbyte_token(
        endpoint=token_conf[ApiConfigKeys.ENDPOINT],
        headers=token_conf[ApiConfigKeys.HEADERS],
        conf=token_conf,
    )

    if not bearer_token:
        logger.error(f"Invalid token for {prefix}, skipping downloads.")
        return

    logger.success(f"Received token for {prefix}")

    for conf in loader.get_configs(datakeys):
        conf[ApiConfigKeys.HEADERS][HeaderKeys.AUTH] = f"Bearer {bearer_token}"
        _download_single(conf, timestamp, output_dir)


def download_without_auth(
    datakeys: list[str],
    loader: ApiConfigLoader,
    timestamp: str,
    output_dir: Path,
) -> None:
    """Lädt Daten ohne Authentifizierung herunter."""
    for conf in loader.get_configs(datakeys):
        _download_single(conf, timestamp, output_dir)