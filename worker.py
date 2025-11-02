### Receive a job ID link to a record of Job table

## Do EL on this table

from meteo_jobs.logger import get_logger
from fastapi import FastAPI
from meteo_jobs.server.routes_worker import router

import os

logger = get_logger(__name__)

API_ID = os.getenv("API_ID")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWD = os.getenv("DB_PASSWD")

app = FastAPI()
logger.info(router)
app.include_router(router)





if __name__ == "__main__":

    logger.info("Extract and Load Station starts")

    import uvicorn
    uvicorn.run("worker:app", host="0.0.0.0", port=8000, reload=True)

    logger.info("Extract and Load ends")
