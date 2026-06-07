FROM python:3.12-slim

WORKDIR /app

# MSSQL sürücüsü (gerçek SambaPOS bağlantısı için). Demo modunda da sorun çıkarmaz.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg2 unixodbc-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kod
COPY backend/ ./backend/
COPY frontend/ ./frontend/

WORKDIR /app/backend
ENV USE_SAMPLE_DATA=true REFRESH_MINUTES=30 HISTORY_DAYS=30
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
