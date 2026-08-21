# Dockerfile 
FROM python:3.13-slim

# Install dependencies
RUN apt-get update && apt-get install -y python3-venv && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app

# Set working directory
WORKDIR /app

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8788

# Entry point
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8788"]