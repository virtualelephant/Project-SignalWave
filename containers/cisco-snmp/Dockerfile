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
COPY snmp_to_influx.py /app/snmp_to_influx.py
COPY devices.txt /app/devices.txt

# CMD ["python", "snmp_to_influx.py"]
CMD ["tail", "-f", "/dev/null"]