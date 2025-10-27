from dataclasses import dataclass

@dataclass
class Job:
    job_id: int | None
    job_name: str
    table_name: str
    last_compute: str
