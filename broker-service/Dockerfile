# Use Python 3.12 slim image as base
FROM docker.io/library/python:3.12-slim
# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /broker-service && mkdir -p /common-components
COPY /broker-service /broker-service
COPY /common-components /common-components
RUN pip install debugpy && pip install -e /broker-service && pip install -e /common-components

# Expose the port the app runs on and debug port
EXPOSE 8001

# Command to run the application
CMD ["sh", "-c", "broker-service"]