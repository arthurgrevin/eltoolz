from dataclasses import dataclass
from enum import Enum
from .connector_type import ExtractType, LoadType


class JobType(Enum):
    EL_STATION = "el_station"
    EL_METEO = "el_meteo"
    ADD_METEO_JOB = "add_meteo_job"

@dataclass
class Job:
    job_id: int | None
    job_name: JobType
    table_name: str
    load_connector: LoadType
    extract_connector: ExtractType
    options: dict
    last_compute: str
