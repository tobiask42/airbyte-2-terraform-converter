from typing import get_type_hints, Any, cast
from collections.abc import Callable
from core_config.custom_types import AirbyteConnection, AirbyteDestination, AirbyteSource, PythonToHclFunc

def get_optional_field_names(typed_dict_type: type) -> frozenset[str]:
    """
    Gibt die set von Feldern zurück, die im TypedDict als NotRequired markiert sind.
    """
    # Neuere Python-Versionen unterstützen __required_keys__ und __optional_keys__
    # Fallback: Annahme, dass alle Keys die KEINE Required sind, optional sind.
    if hasattr(typed_dict_type, '__optional_keys__'):
        opt = getattr(typed_dict_type, '__optional_keys__')
        return opt
    hints = get_type_hints(typed_dict_type)
    # Annahme: Required werden explizit gelistet.
    if hasattr(typed_dict_type, '__required_keys__'):
        all_fields = set(hints.keys())
        req = getattr(typed_dict_type, '__required_keys__')
        return frozenset(all_fields - req)
    # Falls alles nicht funktioniert, muss man ggf. manuell listen
    raise ValueError("Could not identify optional fields for TypedDict")


def get_required_field_names(typed_dict_type: type) -> frozenset[str]:
    """
    Gibt die set von Feldern zurück, die im TypedDict als Required markiert sind.
    """
    if hasattr(typed_dict_type, '__required_keys__'):
        req = getattr(typed_dict_type, '__required_keys__')
        return cast(frozenset[str], req)
    hints = get_type_hints(typed_dict_type)
    # Annahme: alles required (legacy), falls keine NotRequired
    return frozenset(hints.keys())


def get_output_fields(src: AirbyteSource|AirbyteDestination|AirbyteConnection, 
                     typed_dict_type: type, 
                     ignore_fields: frozenset[str]|None = None,
                     include_optionals: bool = True,
                     include_required: bool = False
                    ) -> dict[str,Any]:
    """
    Extrahiert aus einem TypedDict-ähnlichen dict alle Felder, die entweder optional oder required
    sind, jedoch nicht in einer ignore_fields-Liste stehen.
    """
    if ignore_fields is None:
        ignore_fields = frozenset()
    required:frozenset[str] = get_required_field_names(typed_dict_type)
    optionals: frozenset[str] = get_optional_field_names(typed_dict_type)
    out:dict[str,Any] = {}
    for key, val in src.items():
        if key in ignore_fields:
            continue
        if include_optionals and key in optionals:
            out[key] = val
        elif include_required and key in required:
            out[key] = val
    return out

def get_terraform_optional_fields(src: AirbyteSource|AirbyteDestination|AirbyteConnection, 
                                 typed_dict_type: type, 
                                 python_to_hcl_func:PythonToHclFunc, 
                                 field_name_conv:Callable[[str],str],
                                 deprecated_keys:frozenset[str]
                                 ) -> str:
    """
    Gibt die als Terraform-Konfig nutzbaren optionalen (und nicht ignorierten) Felder eines Dicts als formatierten String zurück.
    """
    optionals = get_output_fields(src, typed_dict_type)
    lines:Any = []
    for key, val in sorted(optionals.items()):
        outkey = field_name_conv(key)
        if outkey in deprecated_keys:
            continue
        valstr: str = python_to_hcl_func(val)
        lines.append(f"  {outkey} = {valstr}")
    optional_fields = "\n".join(lines)
    return optional_fields