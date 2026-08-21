# Dockerfile – minimal image for the Hermes Task Queue FastAPI server
FROM python:3.13-slim

# Install any needed OS packages (curl for debugging)
RUN apt-get update && apt-get install -y --no-install-recommends curl python3-venv && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire project (excluding .git via .dockerignore if present)
COPY . /app

# Install hermes agent properly
RUN pip install --break-system-packages hermes-agent

# Install app dependencies
RUN pip install --break-system-packages -r requirements.txt

# Expose the API port
EXPOSE 8788

# Run entrypoint script (starts both worker and server)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]