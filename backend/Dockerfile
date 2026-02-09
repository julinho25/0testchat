FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/src /app/src
COPY backend/migrations /app/migrations
COPY backend/alembic.ini /app/alembic.ini
COPY backend/seed /app/seed

ENV PYTHONPATH=/app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
