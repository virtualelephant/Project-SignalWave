FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential snmp \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your script
COPY snmp_to_influx.py .

# Install Python dependencies
RUN pip install --no-cache-dir \
    pysnmp==4.4.12 \
    influxdb-client==1.40.0 \
    pyasn1==0.4.8

# CMD ["python", "snmp_to_influx.py"]
CMD ["tail", "-f", "/dev/null"]