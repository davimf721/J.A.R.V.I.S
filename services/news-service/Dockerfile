FROM python:3.11-slim

WORKDIR /app

COPY services/news-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/news-service . 
COPY shared /shared


EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8002/health')" || exit 1

CMD ["python", "main.py"]
