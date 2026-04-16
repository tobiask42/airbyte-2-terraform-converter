from typing import Protocol, TypedDict, NotRequired, Required, Any

class HttpHeaders(TypedDict, total=False):
    accept: str
    content_type: str
    authorization: NotRequired[str]

class ApiConfig(TypedDict):
    name: str
    endpoint: str
    filename: str
    headers: HttpHeaders
    data: NotRequired[str]
    next_key: NotRequired[str]
    items_key: NotRequired[str]

class AirbyteSource(TypedDict):
    # Required (according to docs)
    name: Required[str]
    workspaceId: Required[str]
    configuration: Required[dict[str, Any]]
    # Optional
    definitionId: NotRequired[str]
    resourceAllocation: NotRequired[str]
    secretId: NotRequired[str]
    # Read Only
    # sourceId (String)
    # createdAt (Number)
    # sourceType (String)

class AirbyteDestination(TypedDict):
    # Required (according to docs)
    configuration: Required[dict[str, Any]]
    name: Required[str]
    workspaceId: Required[str]
    # Optional
    definitionId: NotRequired[str]
    resourceAllocation: NotRequired[str]
    # Read Only
    # destinationId (String)
    # destinationType (String)
    # createdAt (Number)

class AirbyteConnection(TypedDict):
    # Required (according to docs)
    destinationId: Required[str]
    sourceId: Required[str]
    # Optional
    connectionId: NotRequired[str]
    name: NotRequired[str]
    status: NotRequired[str]
    tags: NotRequired[list[dict[str, Any]]]
    schedule: NotRequired[dict[str, Any]]
    dataResidency: NotRequired[str]
    configurations: NotRequired[dict[str, Any]]
    nonBreakingSchemaUpdatesBehavior: NotRequired[str]
    namespaceDefinition: NotRequired[str]
    prefix: NotRequired[str]
    # Read-Only
    # connectionId (String)
    # createdAt (Number)
    # statusReason (String)
    # workspaceId (String)

HclInputType = dict[str, Any]| list[str] | str | bool | int | float | None

class PythonToHclFunc(Protocol):
    def __call__(self, obj: HclInputType, indent: int = 2, level: int = 0) -> str: ...