# Base image
FROM python:3.9-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies for RRDtool
RUN apt-get update && apt-get install -y \
    rrdtool \
    librrd-dev \
    python3-dev \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY rrd-reader.py /app/

# Create necessary directories
RUN mkdir -p /app/rrd_files

# Run the script
CMD ["python", "rrd-reader.py"]
