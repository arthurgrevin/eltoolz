from fastapi.testclient import TestClient
from worker import app  # ou from meteo_jobs.server.main import app si package
from meteo_jobs.logger import get_logger

logger = get_logger(__name__)

client = TestClient(app)

def test_post_job_success():
    payload = {"job_id": 1}
    response = client.post("/job", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    logger.info(json_data)
    assert json_data["job_id"] == 1
