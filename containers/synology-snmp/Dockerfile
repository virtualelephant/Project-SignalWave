FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential snmp \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
pysnmp==4.4.12 \
influxdb-client==1.40.0 \
pyasn1==0.4.8

# Set working directory
WORKDIR /app

# Copy custom files
COPY . .

# Default command to run the script
CMD ["sh", "-c", "python /app/synology_snmp_polling.py"]