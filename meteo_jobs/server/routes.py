from fastapi import APIRouter
from .models import JobRequest, JobResponse

router = APIRouter()

@router.post("/job", response_model=JobResponse)
def get_job(request: JobRequest):
    return request.job_id
