import httpx
from loguru import logger
import core_config.static_values as constants
from core_config.custom_types import ApiConfig, HttpHeaders
from core_config.custom_dataclasses import ApiConfigKeys
import json

def get_airbyte_token(endpoint: str, headers:HttpHeaders, conf:ApiConfig) -> str|None:
    """
    Holt einen Bearer Token via POST von Airbyte Auth Endpoint.
    conf['data'] ist ein JSON-String.
    """
    logger.info("Creating body")
    raw_data = conf.get(ApiConfigKeys.DATA)
    if raw_data is None:
        logger.error(f"Configuration for Authentication is not set up correctly. ApiConfig object contains no value for key {ApiConfigKeys.DATA}")
        return None
    httpx_headers:dict[str,str] = {k: v for k, v in headers.items() if isinstance(v, str)}
    body = json.loads(raw_data)
    response = httpx.post(endpoint, json=body, headers=httpx_headers)
    logger.info(f"Response Status: {response.status_code}")
    if response.status_code != 200:
        logger.error(f"Response content: {response.text}")
        return None
    response_data = response.json()
    return response_data.get(constants.TOKEN_RESPONSE_ACCESS_KEY)