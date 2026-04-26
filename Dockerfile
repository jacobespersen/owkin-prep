FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY app/__init__.py ./app/__init__.py
RUN pip install --no-cache-dir .

COPY data/ ./data/
COPY app/ ./app/

# Run as a non-root user to limit blast radius if the app is ever exploited.
RUN groupadd --system --gid 1000 appuser \
 && useradd --system --uid 1000 --gid appuser --no-create-home appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]




