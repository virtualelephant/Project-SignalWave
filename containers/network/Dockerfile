FROM debian:bullseye-slim

RUN apt-get update && \
    apt-get install -y snmp && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"]