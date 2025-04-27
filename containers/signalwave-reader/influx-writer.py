import pika
import os
import logging
import json
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions

# Configure structured logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "influx-writer-service",
        }
        return json.dumps(log_record)

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq.signalwave.svc.cluster.local')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'deploy')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'VMware123!')
QUEUE_NAME = os.getenv('RABBITMQ_QUEUE', 'signalwave')

# InfluxDB Configuration
INFLUX_URL = os.getenv('INFLUX_URL', 'http://influxdb.services.svc.cluster.local:8086')
INFLUX_TOKEN = os.getenv('INFLUX_TOKEN', 'my-token')
INFLUX_ORG = os.getenv('INFLUX_ORG', 'virtualelephant')
INFLUX_BUCKET = os.getenv('INFLUX_BUCKET', 'monitoring')

# Initialize global RabbitMQ credentials
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

# Global InfluxDB client and write_api with batching
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=WriteOptions(
    batch_size=500,
    flush_interval=5000,
    jitter_interval=2000,
    retry_interval=3000,
    max_retries=5,
    max_retry_delay=30000,
    exponential_base=2
))

def write_to_influx(metrics, timestamp):
    points = []
    for metric_name, value in metrics.items():
        if value is not None:
            point = (
                Point("signalwave_metrics")
                .tag("metric_name", metric_name)
                .field("value", float(value))
                .time(timestamp, WritePrecision.S)
            )
            points.append(point)

    if points:
        write_api.write(bucket=INFLUX_BUCKET, record=points)
        logger.info(f"Wrote {len(points)} metrics to InfluxDB")

def process_messages():
    logger.info("Starting to process RabbitMQ messages...")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments={"x-queue-type": "quorum"})
        logger.info("Successfully connected to RabbitMQ and declared queue")

        for method, properties, body in channel.consume(queue=QUEUE_NAME, inactivity_timeout=10):
            if body is None:
                break  # Exit consume after inactivity timeout
            try:
                message = json.loads(body)
                timestamp = int(time.mktime(time.strptime(message["timestamp"], "%Y-%m-%d %H:%M:%S")))
                metrics = message["metrics"]
                write_to_influx(metrics, timestamp)
                channel.basic_ack(method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    except Exception as e:
        logger.error(f"Error connecting to RabbitMQ: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()

def main():
    logger.info("Starting Influx Writer Service...")
    try:
        while True:
            process_messages()
            logger.info("Sleeping for 5 minutes before next iteration...")
            time.sleep(300)
    finally:
        if client:
            client.close()
            logger.info("Closed InfluxDB client.")

if __name__ == "__main__":
    main()
