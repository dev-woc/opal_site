FROM python:3.11-slim

WORKDIR /app

# System deps: build tools + chromadb (sqlite)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Install all deps with --prefer-binary to skip compilation where possible
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefer-binary --timeout 300 -r requirements.txt

# Copy backend source
COPY backend/ ./backend/
COPY .env.example .env.example

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
