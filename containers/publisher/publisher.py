import pika
import time
import random
import os
import logging
import json
import socket
import argparse
import requests
from prometheus_client import start_http_server, Counter, Histogram, Summary, Gauge

# Configure structured JSON logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "publisher-service",
        }
        return json.dumps(log_record)

# Logging setup
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq.services.svc.cluster.local')
rabbitmq_port_env = os.getenv('RABBITMQ_PORT', '5672')
if rabbitmq_port_env.startswith('tcp://'):
    RABBITMQ_PORT = int(rabbitmq_port_env.split(":")[-1])
else:
    RABBITMQ_PORT = int(rabbitmq_port_env)
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'deploy')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'VMware123!')
QUEUE_NAME = os.getenv('RABBITMQ_QUEUE', 'signalwave')
MESSAGE_RATE = float(os.getenv('MESSAGE_RATE', 1.0))

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

parser = argparse.ArgumentParser(description="Publisher Service")
parser.add_argument('--url', type=str, default="https://virtualelephant.com", help="Target website for URL metrics")
args = parser.parse_args()

# Prometheus Metrics
latency_histogram = Histogram('http_request_latency_seconds', 'HTTP request latency to target site')
dns_resolution_time = Summary('dns_resolution_time_seconds', 'Time taken to resolve DNS')
http_response_codes = Counter('http_response_code_count', 'Count of HTTP response codes', ['code'])
network_packet_loss = Gauge('network_packet_loss_percentage', 'Packet loss percentage')
jitter_gauge = Gauge('network_latency_jitter_seconds', 'Network latency jitter')
request_size = Summary('http_request_size_bytes', 'HTTP request size in bytes')
response_size = Summary('http_response_size_bytes', 'HTTP response size in bytes')

logger.info("Exposing Prometheus metrics to be scraped by an external server")
start_http_server(8080)  # Exposes metrics on port 8080

def create_connection():
    retry_delay = 5
    max_delay  = 60
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=RABBITMQ_HOST, 
                port=RABBITMQ_PORT, 
                credentials=credentials
            ))
            logger.info("Successfully connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.error({"error": str(e), "message": f"Retrying connection in {retry_delay} seconds..."})
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)

def measure_metrics():
    metrics = {}
    target_url = args.url

    # Measure DNS resolution time
    start_time = time.time()
    try:
        socket.gethostbyname(target_url.split("//")[-1])
        dns_time = time.time() - start_time
        dns_resolution_time.observe(dns_time)
        metrics['dns_resolution_time'] = dns_time
    except socket.gaierror as e:
        logger.error({"error": "DNS resolution failed", "exception": str(e)})
        metrics['dns_resolution_time'] = None

    # Measure HTTP latency and response
    start_time = time.time()
    try:
        response = requests.get(target_url, timeout=5)
        latency = time.time() - start_time
        latency_histogram.observe(latency)
        http_response_codes.labels(code=str(response.status_code)).inc()
        metrics['http_latency'] = latency
        metrics['http_response_code'] = response.status_code
        metrics['request_size'] = len(response.request.body or b'')
        metrics['response_size'] = len(response.content)
        request_size.observe(metrics['request_size'])
        response_size.observe(metrics['response_size'])
    except requests.RequestException as e:
        logger.error({"error": "HTTP request failed", "exception": str(e)})
        metrics['http_latency'] = None
        metrics['http_response_code'] = None

    # Simulate packet loss and jitter (for demo purposes)
    metrics['packet_loss'] = random.uniform(0, 5)  # Random packet loss percentage
    metrics['jitter'] = random.uniform(0, 0.1)  # Random jitter in seconds
    network_packet_loss.set(metrics['packet_loss'])
    jitter_gauge.set(metrics['jitter'])

    return metrics

def main():
    connection = create_connection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments={"x-queue-type": "quorum"})
    logger.info("Successfully connected to RabbitMQ and declared queue")

    try:
        logger.info("Starting metric publisher with a 5-minute interval")
        while True:
            metrics = measure_metrics()
            message = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                "metrics": metrics,
            }
            body = json.dumps(message)
            channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=body)
            logger.info({"action": "publish", "message": message})

            # Wait 5 minutes
            time.sleep(300)
    except KeyboardInterrupt:
        logger.info("Shutting down publisher...")
    finally:
        if connection.is_open:
            connection.close()
            logger.info("Connection to RabbitMQ closed")

if __name__ == "__main__":
    main()
