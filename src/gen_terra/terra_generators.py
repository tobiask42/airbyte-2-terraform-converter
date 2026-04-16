from core_config.custom_dataclasses import(
     MappingPaths, 
     TemplatePaths,
     InputFilePatterns,
     CustomPaths,
     AirbyteKeysCamel,
     AirbyteMappingKeys,
     ResourceIDs
)
from core_config.custom_types import AirbyteSource, AirbyteConnection, AirbyteDestination
from core_config.dynamic_values import SRC_DEPRECATED_KEYS, DEST_DEPRECATED_KEYS, CONN_DEPRECATED_KEYS
import core_config.static_values as constants
from .terra_gen_core import TerraformGenerator


class SourceTerraformGenerator(TerraformGenerator):
    def __init__(self):
        super().__init__(
            data_pattern=InputFilePatterns.DATA_SOURCES,
            template_path=TemplatePaths.SOURCE_TEMPLATE,
            output_dir=CustomPaths.TERRAFORM_PATH,
            tf_vars_path=MappingPaths.TF_VARIABLES,
            deprecated_keys=SRC_DEPRECATED_KEYS,
            entry_type=AirbyteSource,
            mapping_path=MappingPaths.SOURCE_TO_AIRBYTE_MAPPING,
            resource_type_key=AirbyteKeysCamel.SOURCE_TYPE,
            custom_resource_type=constants.CUSTOM_AIRBYTE_SRC,
            import_id_key=ResourceIDs.sourceId
        )

    @property
    def template_key_map(self) -> dict[str,str]:
        return constants.TERRAFORM_KEY_MAPPINGS[AirbyteMappingKeys.SOURCE]

class DestinationTerraformGenerator(TerraformGenerator):
    def __init__(self):
        super().__init__(
            data_pattern=InputFilePatterns.DATA_DESTINATION,
            template_path=TemplatePaths.DESTINATION_TEMPLATE,
            output_dir=CustomPaths.TERRAFORM_PATH,
            tf_vars_path=MappingPaths.TF_VARIABLES,
            deprecated_keys=DEST_DEPRECATED_KEYS,
            entry_type=AirbyteDestination,
            mapping_path=MappingPaths.DESTINATION_TO_AIRBYTE_MAPPING,
            resource_type_key=AirbyteKeysCamel.DESTINATION_TYPE,
            custom_resource_type=constants.CUSTOM_AIRBYTE_DEST,
            import_id_key=ResourceIDs.destinationId
        )
    
    @property
    def template_key_map(self) -> dict[str,str]:
        return constants.TERRAFORM_KEY_MAPPINGS[AirbyteMappingKeys.DESTINATION]

class ConnectionTerraformGenerator(TerraformGenerator):
    def __init__(self):
        super().__init__(
            data_pattern=InputFilePatterns.DATA_CONNECTION,
            template_path=TemplatePaths.CONNECTION_TEMPLATE,
            output_dir=CustomPaths.TERRAFORM_PATH,
            tf_vars_path=MappingPaths.TF_VARIABLES,
            deprecated_keys=CONN_DEPRECATED_KEYS,
            entry_type=AirbyteConnection,
            mapping_path=None,
            resource_type_key=None,
            custom_resource_type=constants.AIRBYTE_CONN,
            import_id_key=ResourceIDs.connectionId
        )

    @property
    def template_key_map(self)->dict[str,str]:
        return constants.TERRAFORM_KEY_MAPPINGS[AirbyteMappingKeys.CONNECTION]