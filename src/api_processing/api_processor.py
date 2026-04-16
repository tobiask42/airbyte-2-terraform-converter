from datetime import datetime
from dotenv import load_dotenv
from core_config.custom_dataclasses import PATHS
from core_config.static_values import TIMESTAMP_PATTERN
from api_processing.get_airbyte_data import prepare_output_dirs, load_api_selection, group_keys, download_with_auth, download_without_auth
from loguru import logger
from api_processing.api_config_loader import ApiConfigLoader

def download_from_airbyte_api() -> None:
    env_path = PATHS.ENV_FILE
    logger.debug(f"Loading dotenv from: {env_path}")
    logger.debug(f"File exists: {env_path.exists()}")
    load_dotenv(env_path,override=False)
    timestamp = datetime.now().strftime(TIMESTAMP_PATTERN)
    _, output_dir = prepare_output_dirs(timestamp)

    tokens_map, datakeys = load_api_selection()
    withauth, noauth = group_keys(tokens_map, datakeys)

    loader = ApiConfigLoader()

    for prefix, keys in withauth.items():
        download_with_auth(prefix, keys, tokens_map, loader, timestamp, output_dir)

    if noauth:
        download_without_auth(noauth, loader, timestamp, output_dir)

    logger.success("Successfully finished.")