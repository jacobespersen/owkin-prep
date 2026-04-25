FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY app/__init__.py ./app/__init__.py
RUN pip install --no-cache-dir .

COPY data/ ./data/
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]



