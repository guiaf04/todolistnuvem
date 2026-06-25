# Dockerfile da aplicação To‑Do (Flask + Gunicorn)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dependência de runtime do psycopg2-binary
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY app /app/app
COPY wsgi.py /app/wsgi.py

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "wsgi:app"]
