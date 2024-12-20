# Use a slim Python image for smaller footprint
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system-level build dependencies, if any (optional)
# Example: RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage build cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for Python and local configuration
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Default command: run bash (for dev), override in CI/CD as needed
CMD [ "bash" ]