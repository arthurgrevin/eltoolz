from dataclasses import dataclass

@dataclass
class Job:
    job_id: int | None
    job_name: str
    table_name: str
    load_connector: str
    extract_connector: str
    options: dict
    last_compute: str
