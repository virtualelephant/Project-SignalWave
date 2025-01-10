# Base image
FROM python:3.9-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies for RRDtool
RUN apt-get update && apt-get install -y \
    rrdtool \
    python3-rrdtool \
    librrd-dev \
    python3-dev \
    gcc \
    cron \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# Set up the directories
RUN mkdir -p /app/rrd_files /app/graphs

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the graph generation script
COPY generate-graphs.py /app/

# Run the script in an infinite loop
CMD ["python3", "/app/generate-graphs.py"]

