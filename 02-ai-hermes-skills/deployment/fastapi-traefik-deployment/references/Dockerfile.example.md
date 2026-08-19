# Dockerfile – FastAPI behind Traefik
# ------------------------------------------------------------
# This file lives under the fastapi‑traefik‑deployment skill.
# It shows the exact Dockerfile you should copy into the FastAPI
# project root (e.g. /home/aldo/dev/02-ai-taskqueue).
# ------------------------------------------------------------
FROM python:3.13-slim

# Install any OS‑level utilities you need (curl is useful for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project (excluding .git via .dockerignore if you like)
COPY . /app

# Create a virtual environment and install dependencies
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI port (internal to the Docker network)
EXPOSE 8788

# Run uvicorn from the venv, listening on all interfaces
CMD ["/app/.venv/bin/uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8788"]
