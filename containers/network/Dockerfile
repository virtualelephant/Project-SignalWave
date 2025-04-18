FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential snmp snmp-mibs-downloader \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your script
COPY snmp_to_influx.py .

# Install Python dependencies
RUN pip install --no-cache-dir pysnmp influxdb-client

# Run the script by default (optional — remove ENTRYPOINT for manual exec)
#ENTRYPOINT ["python", "snmp_to_influx.py"]


CMD ["tail", "-f", "/dev/null"]