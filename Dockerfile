FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# dépendances système nécessaires pour psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# copier requirements si présent (facultatif mais recommandé)
COPY requirements.txt /app/requirements.txt

RUN if [ -s /app/requirements.txt ]; then \
        pip install --no-cache-dir -r /app/requirements.txt ; \
    else \
        pip install --no-cache-dir fastapi uvicorn[standard] psycopg2-binary returns ; \
    fi

# Ne copier que worker.py, __init__.py et le package meteo_jobs
COPY worker.py __init__.py meteo_jobs/ /app/

EXPOSE 80

CMD ["uvicorn", "worker:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "info"]
