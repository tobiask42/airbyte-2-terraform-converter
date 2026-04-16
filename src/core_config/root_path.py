from pathlib import Path
from loguru import logger
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).parents[2] # airbyte-2-terraform-converter
logger.debug(f"Project Root: {PROJECT_ROOT}")