FROM python:3.10-slim

RUN apt-get update && apt-get install -y fping && \
    pip install requests && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY fping_to_influx.py /app/fping_to_influx.py
COPY targets.txt /app/targets.txt

#ENTRYPOINT ["python", "/app/fping_to_influx.py"]
CMD ["tail", "-f", "/dev/null"]