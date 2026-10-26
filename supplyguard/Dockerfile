FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATABASE_PATH=/data/supplyguard.db APP_HOST=0.0.0.0 APP_PORT=5050 APP_RELOAD=false
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /data && useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app /data
USER appuser
EXPOSE 5050
CMD ["python", "run.py"]
