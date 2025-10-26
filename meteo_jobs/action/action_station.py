from .action import Action
from typing import Iterator
from meteo_jobs.models import Station
from meteo_jobs.logger import get_logger
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

logger = get_logger(__name__)

class ActionStation(Action):

    def __init__(self):
        """"""

    def _launch_meteo_extract(self, station_name):
        """Launch a process to start extract meteo for one station"""
        log_file = f"{station_name}_extract.log"
        cmd = ["python3.12", "start_EL_meteo.py", "--station", station_name]
        logger.info(f"Start EL for {station_name}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        with open(log_file, "w") as f:
            result = subprocess.run(
                cmd,
                stdout=f,        # redirige stdout vers le fichier
                stderr=subprocess.STDOUT,  # redirige stderr aussi
                text=True
            )
        logger.info(f"End EL for {station_name}")
        return station_name, result.returncode, log_file, result.stderr



    def execute(self, records: Iterator[Station]) -> Iterator[Station]:
        with ProcessPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._launch_meteo_extract, station.id_nom): station
                for station in records
            }

        for future in as_completed(futures):
                station = futures[future]
                name, code, out, err = future.result()
                logger.info(f"{name} is finished with {code}")
                if err:
                     logger.error(f"{name} error with {err}")
                yield station
