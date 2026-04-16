from typing import Any, Final

CUSTOM_AIRBYTE_SRC:Final[str] = "airbyte_source_custom"
CUSTOM_AIRBYTE_DEST:Final[str] = "airbyte_destination_custom"
AIRBYTE_CONN: Final[str] = "airbyte_connection"
API_DATAKEY: Final[str] = "data"
DATA_PREFIX: Final[str] = "data_"
API_SELECTION_DATAKEY: Final[str] = "data"
API_SELECTION_TOKENSKEY: Final[str] = "tokens"
TOKEN_RESPONSE_ACCESS_KEY: Final[str] = "access_token"

TF_COMMANDS: Final[tuple[str, ...]] = ("var.", "local.", "module.")

TIMESTAMP_PATTERN: Final[str] = "%Y%m%d_%H%M%S"

ENV_PREFIX: Final[str] = "AB2TF_" # Prefix for system environment variables

IMPORTS_PREFIX: Final[str] = "imports_"

TF_SUFFIX: Final[str] = ".tf"

TERRAFORM_KEY_MAPPINGS:Final[dict[str,Any]] = {
    "source": {
        "name": "name"
    },
    "destination": {
        "name": "name"
    },
    "connection": {
        "name": "name",
        "destination_id": "destinationId",
        "source_id": "sourceId"
    }
}