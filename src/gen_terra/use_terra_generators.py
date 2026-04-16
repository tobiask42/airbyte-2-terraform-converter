from .terra_generators import SourceTerraformGenerator, DestinationTerraformGenerator, ConnectionTerraformGenerator
from core_config.custom_dataclasses import CustomPaths
from loguru import logger

def generate_terra_src() -> bool:  
    try:  
        SourceTerraformGenerator().generate(CustomPaths.DATA_DIR)  
        return True  
    except Exception:  
        logger.exception("Failed to generate source tf files")  
        return False

def generate_terra_dest() -> bool:
    try:
        DestinationTerraformGenerator().generate(CustomPaths.DATA_DIR)
        return True
    except Exception:
        logger.exception("Failed to generate destination tf")
        return False

def generate_terra_conn():
    try:
        ConnectionTerraformGenerator().generate(CustomPaths.DATA_DIR)
        return True
    except Exception:
        logger.exception("Failed to generate connection tf")
        return False

def generate_imports() -> bool:  
    success = True  
    for generator_cls, label in [  
        (SourceTerraformGenerator, "sources"),  
        (DestinationTerraformGenerator, "destinations"),  
        (ConnectionTerraformGenerator, "connections"),  
    ]:  
        try:  
            generator_cls().generate_imports(CustomPaths.DATA_DIR)  
        except Exception:  
            logger.exception(f"Failed to generate imports for {label}")  
            success = False  
    return success