FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copying requirements first — Docker caches this layer
# So code changes don't re-install packages every build
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy all source code
COPY . .

# HuggingFace Spaces requires port 7860
ENV PORT=7860
ENV HOST=0.0.0.0
ENV WORKERS=2

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run from /app, import server.app as a module
CMD ["sh", "-c", "uvicorn server.app:app --host $HOST --port $PORT --workers $WORKERS"]