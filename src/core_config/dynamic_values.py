from .custom_dataclasses import MappingPaths
import json
from typing import Final

with MappingPaths.CONN_DEPRECATED.open() as f:
    conn_deprecated_keys = json.load(f)
with MappingPaths.SRC_DEPRECATED.open() as f:
    src_deprecated_keys = json.load(f)
with MappingPaths.DEST_DEPRECATED.open() as f:
    dest_deprecated_keys = json.load(f)

CONN_DEPRECATED_KEYS:Final[frozenset[str]] = frozenset(conn_deprecated_keys)
SRC_DEPRECATED_KEYS:Final[frozenset[str]] = frozenset(src_deprecated_keys)
DEST_DEPRECATED_KEYS:Final[frozenset[str]] = frozenset(dest_deprecated_keys)