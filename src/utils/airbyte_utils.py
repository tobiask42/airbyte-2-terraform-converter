import json
from typing import Any
from urllib.parse import urlparse, urljoin
import core_config.static_values as constants
from core_config.custom_dataclasses import MappingPaths, RegexPatterns
from core_config.custom_types import AirbyteSource as AirSrc, AirbyteDestination as AirDest, AirbyteConnection as AirConn, HclInputType
from pathlib import Path
from loguru import logger
import shutil
import datetime

def merge_next_with_base(next_url:str, base_url:str):
    next_parsed = urlparse(next_url)
    path_and_query = next_parsed.path
    if next_parsed.query:
        path_and_query += f"?{next_parsed.query}"
    return urljoin(base_url, path_and_query)

# Key-Mapping für sensitive Variablen
with MappingPaths.TF_SENSITIVE_KEYS.open() as f:
    SENSITIVE_KEYS = json.load(f)

with MappingPaths.TF_VARIABLES.open() as f:
    HCL_VARIABLES = {k.lower(): v for k, v in json.load(f).items()}


def python_to_hcl(obj:HclInputType, indent:int=2, level:int=0) -> str:
    sp = " " * (indent * level)
    if isinstance(obj, dict):
        if not obj:
            return "{ }"
        lines = ["{"]
        for k, v in obj.items():
            key = camel_to_snake(k)
            value_str = None

            if key in HCL_VARIABLES:
                ersatz = HCL_VARIABLES[key]
                if ersatz.startswith(constants.TF_COMMANDS):
                    value_str = ersatz
                else:
                    value_str = f'"{ersatz}"'
            elif key in SENSITIVE_KEYS:
                placeholder = SENSITIVE_KEYS[key]
                value_str = f'"{placeholder}"'
            else:
                value_str = python_to_hcl(v, indent, level + 1)

            lines.append(f'{sp}  {key} = {value_str}')
        lines.append(f'{sp}}}')
        return '\n'.join(lines)

    elif isinstance(obj, list):
        if not obj:
            return "[]"
        items = [python_to_hcl(v, indent, level + 1) for v in obj]
        items = [f'{sp}  {item}' for item in items]
        return '[\n' + ',\n'.join(items) + f'\n{sp}]'

    elif isinstance(obj, str):
        if RegexPatterns.HCL_VAR_REFERENCE.match(obj):
            return obj
        safe = obj.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{safe}"'

    elif isinstance(obj, bool):
        return 'true' if obj else 'false'

    elif isinstance(obj, (int, float)):
        return str(obj)

    elif obj is None:
        return "null"


def make_tf_name(src: AirSrc | AirDest | AirConn) -> str:
    if "connectionId" in src:
        # Connection: bevorzugt
        basename = src.get("name", "connection").lower()
        id_part = src.get("connectionId", "")
        if not id_part:
            src_id = src.get("sourceId", "")[:4]
            dest_id = src.get("destinationId", "")[:4]
            id_part = f"{src_id}{dest_id}"
        id_part = id_part[:8]
    elif "destinationId" in src:
        # Destination: hat immer "destinationId", nicht aber "connectionId"
        basename = src.get("name", "destination").lower()
        id_part = src.get("destinationId", "")[:8]
    else:
        # Source: hat immer "sourceId"
        basename = src.get("name", "source").lower()
        id_part = src.get("sourceId", "")[:8]
    basename = RegexPatterns.TF_NAME_CLEAN.sub("_", basename)
    return f"{basename}_{id_part}" if id_part else basename

def camel_to_snake(name:str) -> str:
    """
    Konvertiert CamelCase oder camelCase nach snake_case (z.B. 'workspaceId' → 'workspace_id').
    Ersetzt auch Mehrfach-Großbuchstaben korrekt ('myABCId' → 'my_abc_id').
    """
    s1 = RegexPatterns.CAMEL1.sub(r'\1_\2', name)
    snake = RegexPatterns.CAMEL2.sub(r'\1_\2', s1)
    return snake.lower()

def filter_fields(obj:Any, whitelist:list[str]) -> dict[str,str]:
    result:dict[str,str] = {}
    for key in whitelist:
        new_key = camel_to_snake(key)
        # Mapping aus tf_variables.json geht IMMER vor!
        if new_key in HCL_VARIABLES:
            result[new_key] = HCL_VARIABLES[new_key]
        elif key in obj:
            result[new_key] = obj[key]
    return result

def read_flagfile(flag_path: Path) -> list[str]:
    if not flag_path.exists():
        return []
    try:
        with flag_path.open("r", encoding="utf-8") as f:
            flag_data = json.load(f)
            return flag_data.get("files", [])
    except Exception:
        return []

def write_flagfile(flag_path: Path, files_copied: list[str]) -> None:
    flag_data = {
        "copied_at": datetime.datetime.now().isoformat(),
        "files": files_copied
    }
    with flag_path.open("w", encoding="utf-8") as f:
        json.dump(flag_data, f, indent=2)

def copy_files(sourcefolder: Path, destinationfolder: Path, flagfile: str = ".copied.flag") -> bool:
    flag_path = destinationfolder / flagfile
    already_copied = set(read_flagfile(flag_path))
    all_files = [f for f in sourcefolder.iterdir() if f.is_file()]
    new_files = [f for f in all_files if f.name not in already_copied]

    if not new_files:
        return True

    errors: list[str] = []
    copied_names = set(already_copied)
    for file in new_files:
        dest_file = destinationfolder / file.name
        try:
            shutil.copy2(file, dest_file)
            copied_names.add(file.name)
        except Exception as e:
            logger.error(f"Fehler beim Kopieren von {file}: {e}")
            errors.append(file.name)

    write_flagfile(flag_path, sorted(list(copied_names)))

    if errors:
        logger.error(f"Diese Dateien konnten nicht kopiert werden: {errors}")
        return False

    logger.success(f"{len(new_files)} neue Dateien kopiert.")
    return True

def get_comparators(path: Path, key:str) -> set[str]:
    with path.open() as f:
        json_content = json.load(f)
    comparators: set[str] = set()
    data: list[dict[str,Any]] = json_content[constants.API_DATAKEY]
    for entry in data:
        if key in entry:
            comparators.add(entry[key])
    if len(comparators) != len(data):
        logger.warning(f"Key '{key}' not found in {len(data)-len(comparators)} out of {len(data)} entries.")
    return comparators