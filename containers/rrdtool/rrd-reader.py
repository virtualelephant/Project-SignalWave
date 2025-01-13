import pika
import os
import logging
import json
import time
import rrdtool

# Configure structured logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "rrd-reader-service",
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

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

# Define RRDtool settings
RRD_FOLDER = "/app/rrd_files"
os.makedirs(RRD_FOLDER, exist_ok=True)

def create_rrd(metric_name):
    rrd_file = os.path.join(RRD_FOLDER, f"{metric_name}.rrd")
    if not os.path.exists(rrd_file):
        logger.info(f"Creating RRD database for metric: {metric_name}")

        # Define units for metrics
        metric_units = {
            "dns_resolution_time": "seconds",
            "http_latency": "seconds",
            "http_response_code": "count",
            "request_size": "bytes",
            "response_size": "bytes",
            "packet_loss": "percentage",
            "jitter": "seconds",
        }

        unit = metric_units.get(metric_name, "unknown")

        rrdtool.create(
            rrd_file,
            "--step", "300",  # 5-minute intervals
            "DS:value:GAUGE:600:U:U",  # Data source with unknown min/max
            "RRA:AVERAGE:0.5:1:288",  # Retain 1-day data at 5-min resolution
            "RRA:AVERAGE:0.5:12:168"  # Retain 1-week data at 1-hour resolution
        )

        logger.info(f"Added unit {unit} to RRD database for {metric_name}")
    return rrd_file

def update_rrd(metric_name, value, timestamp):
    rrd_file = create_rrd(metric_name)
    try:
        # Fetch the last update time for the RRD
        last_update = int(rrdtool.info(rrd_file).get("last_update", 0))
        if timestamp <= last_update:
            logger.warning(f"Adjusting timestamp for {metric_name} from {timestamp} to {last_update + 1}")
            timestamp = last_update + 1

        # Update the RRD database with the adjusted timestamp
        rrdtool.update(rrd_file, f"{int(timestamp)}:{value}")
        logger.info(f"Updated RRD for {metric_name} with value {value} at {timestamp}")
    except Exception as e:
        logger.error(f"Error updating RRD for {metric_name}: {e}")

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
                for metric_name, value in metrics.items():
                    if value is not None:  # Ensure value is not None
                        update_rrd(metric_name, value, timestamp)
                channel.basic_ack(method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    except Exception as e:
        logger.error(f"Error connecting to RabbitMQ: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()

def main():
    logger.info("Starting RRD Reader Service...")
    while True:
        process_messages()
        logger.info("Sleeping for 5 minutes before next iteration...")
        time.sleep(300)  # Sleep for 5 minutes

if __name__ == "__main__":
    main()
