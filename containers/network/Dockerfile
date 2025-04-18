FROM debian:bullseye-slim

RUN apt-get update && \
    apt-get install -y snmp && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

MKDIR /app
COPY snmp-to-influxdb.py /app
WORKDIR /app

CMD ["tail", "-f", "/dev/null"]