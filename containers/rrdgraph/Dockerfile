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

# Copy the graph generation script
COPY generate-graphs.py /app/

# Set up a cron job to generate graphs every 5 minutes
RUN \
    echo "*/5 * * * * python3 /app/generate-graphs.py" > /etc/cron.d/generate-graphs && \
    chmod 0644 /etc/cron.d/generate-graphs && \
    crontab /etc/cron.d/generate-graphs

# Start cron as the main process
CMD ["cron", "-f"]

