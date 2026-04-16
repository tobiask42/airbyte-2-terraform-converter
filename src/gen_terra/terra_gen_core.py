from pathlib import Path
import json
from typing import Any, cast
from jinja2 import Template
from loguru import logger
from core_config.custom_types import AirbyteConnection as AirConn, AirbyteDestination as AirDest, AirbyteSource as AirSrc
from core_config.static_values import IMPORTS_PREFIX, TF_SUFFIX
from utils.airbyte_utils import copy_files, python_to_hcl, make_tf_name, camel_to_snake
from utils.custom_types_utils import get_terraform_optional_fields
from core_config.custom_dataclasses import CustomPaths, TemplatePaths

class TerraformGenerator:
    def __init__(self, data_pattern:str,
                template_path:Path,
                output_dir:Path,
                tf_vars_path:Path,
                deprecated_keys:frozenset[str],
                entry_type: type[AirSrc]|type[AirDest]|type[AirConn],
                resource_type_key:str|None,
                mapping_path: Path|None=None,
                custom_resource_type:str|None=None,
                import_id_key:str|None = None):
        self.data_pattern = data_pattern
        self.template = self._load_template(template_path)
        self.output_dir = Path(output_dir)
        self.tf_vars = self._load_json(tf_vars_path)
        self.deprecated_keys = deprecated_keys
        self.mapping = self._load_json(mapping_path) if mapping_path else None
        self.resource_type_key = resource_type_key
        self.custom_resource_type = custom_resource_type
        self.entry_type = entry_type
        self.import_id_key = import_id_key
        self.import_template = self._load_template(TemplatePaths.IMPORT_TEMPLATE)
        if (mapping_path is None) != (resource_type_key is None):
            raise ValueError(
                f"{self.__class__.__name__}: 'mapping_path' und 'resource_type_key'"
                f"müssen beide gesetzt oder beide None sein."
                f"Got: mapping_path={mapping_path}, resource_type_key={resource_type_key}"
            )
        if mapping_path is None:
            logger.debug(
                f"{self.__class__.__name__}: Kein Mapping konfiguriert "
                f"verwende immer '{custom_resource_type}' als resource_type."
            )
    
    @property
    def required_template_keys(self)->dict[str,str]:
        return {}

    @property
    def template_key_map(self) -> dict[str,str]:
        return {}

    @staticmethod
    def _load_json(path:Path) -> Any:
        try:
            with path.open() as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON {path}: {e}")
            return {}

    @staticmethod
    def _load_template(path:Path):
        try:
            with path.open() as f:
                return Template(f.read())
        except Exception as e:
            logger.error(f"Failed to load Template {path}: {e}")
            return Template("")

    def should_skip(self, entry:AirConn|AirDest|AirSrc) -> str|None:
        # Override this in subclasses or inject a filter function
        return

    def build_tf_name(self, entry:AirSrc | AirDest | AirConn):
        return make_tf_name(entry)

    def build_config_string(self, entry:AirSrc | AirDest | AirConn):
        return python_to_hcl(entry.get("configuration", {}), indent=2)

    def resolve_resource_type(self, entry: AirSrc | AirDest | AirConn) -> str:
        if self.mapping and self.resource_type_key:
            entry_type = entry.get(self.resource_type_key)
            if not entry_type:
                return self.custom_resource_type or ""
            logger.debug(f"Entry Type ({self.resource_type_key}): {entry_type}")

            resource_type = self.mapping.get(entry_type)
            if not resource_type:
                logger.warning(
                    f"WARNUNG: '{entry_type}' ist kein bekannter Typ, wird als {self.custom_resource_type} ausgegeben [{entry.get('name','?')}]"
                )
                return self.custom_resource_type or ""
            return resource_type
        return self.custom_resource_type or ""

    def output_filename(self, input_json:Path)->str:
        return input_json.with_suffix('.tf').name

    def postprocess_dir(self, input_json:Path):
        # Output in terra_gen/<timestamp-or-parent>
        return self.output_dir / input_json.parent.name

    def main_files(self)-> Path:
        # Return paths for things that should be copied to each output dir
        return CustomPaths.TERRAFORM_MAIN_FILES

    def process_entry(self, entry:AirSrc | AirDest | AirConn) -> str:
        # Override in child classes if needed
        optional_fields = get_terraform_optional_fields(
            entry,
            self.entry_type,
            python_to_hcl_func=python_to_hcl,  # actual function, not field
            field_name_conv=camel_to_snake,
            deprecated_keys=self.deprecated_keys
        )
        # logger.debug(f"optional_fields: {optional_fields}, type: {type(optional_fields)}")
        return optional_fields

    def render_entry(self,
        entry:AirSrc | AirDest | AirConn,
        resource_type:str,
        tf_name:str,
        config_string:str,
        optional_fields:str
    ):
        template_args = {
            "resource_type": resource_type,
            "tf_name": tf_name,
            "config_string": config_string,
            "optional_fields": optional_fields,
            **self.tf_vars,
        }
        # Jetzt mapping nutzen:
        for tpl_key, json_key in self.template_key_map.items():
            template_args[tpl_key] = entry.get(json_key, "")
        return self.template.render(**template_args)

    def render_import_block(self, resource_type:str, tf_name: str, import_id: str) -> str:
        return self.import_template.render(
            resource_type=resource_type,
            tf_name = tf_name,
            import_id = import_id
        )
    
    def import_filename(self, input_json: Path) -> str:
        return IMPORTS_PREFIX + input_json.with_suffix(TF_SUFFIX).name

    def generate(self, input_dir:Path):
        data_files = list(input_dir.glob(self.data_pattern))
        logger.debug(f"Data pattern: {self.data_pattern}, files found: {data_files}")
        for input_json in data_files:
            entries: list[AirConn|AirDest|AirSrc] = self._load_json(input_json).get("data", [])
            outdir = self.postprocess_dir(input_json)
            outdir.mkdir(parents=True, exist_ok=True)
            copy_files(self.main_files(), outdir)
            out_file = outdir / self.output_filename(input_json)

            with out_file.open("w") as out:
                for entry in entries:
                    if self.should_skip(entry):
                        logger.info(f"Skipped entry due to skip flag: {entry.get('name','?')}")
                        continue
                    tf_name = self.build_tf_name(entry)
                    config_string = self.build_config_string(entry)
                    resource_type = self.resolve_resource_type(entry)
                    optional_fields = self.process_entry(entry)
                    tf_code = self.render_entry(entry, resource_type, tf_name, config_string, optional_fields)
                    out.write(tf_code + "\n\n")
            logger.info(f"Erstellt: {out_file}")

        logger.success(f"Alle Terraform-Einträge ({self.output_dir}) wurden erzeugt!")

    def generate_imports(self, input_dir: Path):  
        if not self.import_id_key:  
            logger.warning("import_id_key nicht gesetzt. Import-Generierung übersprungen.")  
            return  
    
        data_files = list(input_dir.glob(self.data_pattern))  
        for input_json in data_files:  
            raw_data: list[dict[str, Any]] = self._load_json(input_json).get("data", [])  
            outdir = self.postprocess_dir(input_json)  
            outdir.mkdir(parents=True, exist_ok=True)  
    
            out_file = outdir / self.import_filename(input_json)  
            blocks: list[str] = []  
    
            for raw_entry in raw_data:  
                entry = cast(AirSrc | AirDest | AirConn, raw_entry)  
                if self.should_skip(entry):  
                    continue  
    
                import_id = raw_entry.get(self.import_id_key)  
                if not import_id:  
                    logger.warning(  
                        f"'{self.import_id_key}' nicht in Rohdaten für: {raw_entry.get('name', '?')}"  
                    )  
                    continue  
    
                resource_type = self.resolve_resource_type(entry)  
                tf_name = self.build_tf_name(entry)  
                blocks.append(self.render_import_block(resource_type, tf_name, import_id))  
    
            if blocks:  
                with out_file.open("w") as f:  
                    f.write("\n\n".join(blocks) + "\n")  
                logger.info(f"Import-Datei erstellt: {out_file}")  
            else:  
                logger.warning(f"Keine Import-Blöcke generiert für: {input_json.name}")  
    
        logger.success(f"Alle Import-Blöcke ({self.output_dir}) wurden erzeugt!")