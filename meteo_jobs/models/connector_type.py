from enum import Enum

class ExtractType(Enum):
    POSTGRES = "postgres"
    API = "api"
    UNKNOWN = "unknown"

class LoadType(Enum):
    POSTGRES = "postgres"
    UNKNOWN = "unknown"
