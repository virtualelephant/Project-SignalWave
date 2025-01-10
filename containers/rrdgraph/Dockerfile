FROM python:3.9-slim

# Install necessary system packages for RRDTool
RUN apt-get update && apt-get install -y \
    rrdtool \
    python3-rrdtool \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up the directories
RUN mkdir -p /app/rrd_files /app/graphs

# Copy the graph generation script
COPY generate-graphs.py /app/

# Set up a cron job to generate graphs every 5 minutes
RUN apt-get install -y cron && \
    echo "*/5 * * * * python3 /app/generate-graphs.py" > /etc/cron.d/generate-graphs && \
    chmod 0644 /etc/cron.d/generate-graphs && \
    crontab /etc/cron.d/generate-graphs

# Start cron as the main process
CMD ["cron", "-f"]

