from pydantic import BaseModel

class JobRequest(BaseModel):
    job_id: int

class JobResponse(BaseModel):
    job_id: int
    status: str
    name: str
