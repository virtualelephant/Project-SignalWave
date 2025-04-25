FROM python:3.12-slim

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

# Accept a build-time argument for default script (optional)
ARG DEFAULT_SCRIPT=cisco_snmp_polling.py
ENV DEFAULT_SCRIPT=${DEFAULT_SCRIPT}

# Allow passing SCRIPT_NAME at runtime (override DEFAULT_SCRIPT)
ENV SCRIPT_NAME=${DEFAULT_SCRIPT}

# Default command to run the script
CMD ["sh", "-c", "python /app/$SCRIPT_NAME"]