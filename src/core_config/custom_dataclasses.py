from pathlib import Path
from dataclasses import dataclass
from .bootstrap import bootstrap
from .root_path import PROJECT_ROOT
from re import Pattern, compile


@dataclass
class AirbyteKeysCamel():
    SOURCE_TYPE = "sourceType"
    DESTINATION_TYPE = "destinationType"
    NAME = "name"
    SOURCE_ID = "sourceId"
    SOURCE = "source"

@dataclass
class AirbyteMappingKeys():
    SOURCE = "source"
    DESTINATION = "destination"
    CONNECTION = "connection"


@dataclass
class ApiConfigKeys():
    NAME = "name"
    ENDPOINT = "endpoint"
    FILENAME = "filename"
    HEADERS = "headers"
    DATA = "data"
    NEXT_KEY = "next_key"
    ITEMS_KEY = "items_key"

    ENV_RESOLVABLE_FIELDS = frozenset({
        ENDPOINT,
        DATA
    })

@dataclass
class HeaderKeys():
    AUTH = "authorization"
    AUTH_ENV = "authorization_env"

@dataclass
class VarKeys():
    ENDPOINT = "endpoint"
    DATA = "data"

@dataclass(frozen=True)
class CustomPaths():
    CONFIG_PATH = PROJECT_ROOT / "configs"
    DATA_DIR = PROJECT_ROOT / "data"
    TERRAFORM_PATH = PROJECT_ROOT / "terra_gen"
    TERRAFORM_MAIN_FILES: Path = PROJECT_ROOT / "terraform_main_files"
    LOG_PATH = PROJECT_ROOT / "logs"

    @property
    def ENV_FILE(self) -> Path:
        if bootstrap.env_file:
            return self.CONFIG_PATH / bootstrap.env_file
        else:
            raise ValueError("No ENV_FILE_NAME provided.")
    
    @property
    def API_CONFIG(self) -> Path:
        if bootstrap.api_config:
            return self.CONFIG_PATH / bootstrap.api_config
        else:
            raise ValueError("No API_CONFIG_NAME provided.")

    @property
    def API_SELECTION(self) -> Path:
        if bootstrap.api_selection:
            return self.CONFIG_PATH / bootstrap.api_selection
        else:
            raise ValueError("No API_SELECTION_NAME provided.")

PATHS = CustomPaths()

@dataclass
class MappingPaths():
    SOURCE_TO_AIRBYTE_MAPPING = PROJECT_ROOT / "mappings" / "source" / "airbyte_source_type_2_tf.json"
    SRC_DEPRECATED = PROJECT_ROOT / "mappings" / "source" / "airbyte_source_deprecated_keys.json"
    DESTINATION_TO_AIRBYTE_MAPPING = PROJECT_ROOT / "mappings" / "destination" / "airbyte_destination_type_2_tf.json"
    DEST_DEPRECATED = PROJECT_ROOT / "mappings" / "destination/airbyte_destination_deprecated_keys.json"
    CONN_DEPRECATED = PROJECT_ROOT / "mappings" / "connection" / "airbyte_connection_deprecated_keys.json"
    TF_VARIABLES = PROJECT_ROOT / "mappings" / "generic" / "tf_variables.json"
    TF_SENSITIVE_KEYS = PROJECT_ROOT / "mappings" / "generic" / "tf_sensitive_keys.json"


@dataclass
class TemplatePaths():
    SOURCE_TEMPLATE = PROJECT_ROOT / "templates" / "source.j2"
    DESTINATION_TEMPLATE = PROJECT_ROOT / "templates" / "destination.j2"
    CONNECTION_TEMPLATE = PROJECT_ROOT / "templates" / "connection.j2"
    IMPORT_TEMPLATE = PROJECT_ROOT / "templates" / "imports.j2"

@dataclass
class InputFilePatterns:
    DATA_SOURCES:str = f"data_*/sources_ab*_*.json"
    DATA_DESTINATION:str = f"data_*/destinations_ab*_*.json"
    DATA_CONNECTION:str = f"data_*/connections_ab*_*.json"

@dataclass(frozen=True)
class RegexPatterns:
    # Sucht Variablen im Format ${VARIABLENNAME}
    ENV_VAR: Pattern[str] = compile(r"\$\{([A-Z0-9_]+)\}")

    # Für Terraform-Names: alles außer Kleinbuchstaben, Ziffern oder _ wird zu _
    TF_NAME_CLEAN: Pattern[str] = compile(r"[^a-z0-9_]+")

    # Für die Erkennung von Terraform-Var, -Local, -Module (HCL-Variables im String)
    HCL_VAR_REFERENCE: Pattern[str] = compile(r"^(var\.|local\.|module\.)")

    # CamelCase zu snake_case Umwandlung - Erster Teil
    CAMEL1: Pattern[str] = compile(r'(.)([A-Z][a-z]+)')
    # CamelCase zu snake_case Umwandlung - Zweiter Teil
    CAMEL2: Pattern[str] = compile(r'([a-z0-9])([A-Z])')

@dataclass(frozen=True)
class ResourceIDs:
    sourceId:str = "sourceId"
    destinationId:str = "destinationId"
    connectionId: str = "connectionId"