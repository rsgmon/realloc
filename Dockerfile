# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Set up working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy your source code into container
COPY . /app

# Install your package and dev tools
RUN pip install --upgrade pip
RUN pip install -e .[dev]

# Default command: run CLI
ENTRYPOINT ["portfolio-cli"]
