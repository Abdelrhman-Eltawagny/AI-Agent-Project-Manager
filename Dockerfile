FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    CREWAI_TRACING_ENABLED=false \
    OTEL_SDK_DISABLED=true

# build tools: some crewai dependencies compile native extensions
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p outputs

# default: run the self-test on the bundled sample document
CMD ["python", "main.py", "--test"]
