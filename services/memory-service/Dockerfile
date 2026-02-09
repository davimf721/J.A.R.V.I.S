FROM python:3.11-slim

WORKDIR /app

# Instalar dependências de compilação para hnswlib e outras bibliotecas C
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY services/memory-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/memory-service . 
COPY shared /shared

EXPOSE 8005

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8005/health')" || exit 1

CMD ["python", "main.py"]
