FROM python:3.11-slim

WORKDIR /app

COPY services/llm-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/llm-service . 
COPY shared /shared

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8001/health')" || exit 1

CMD ["python", "main.py"]
