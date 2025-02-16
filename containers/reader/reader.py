import pika
import os
import json
import logging

# Configure structured logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "reader-service",
        }
        return json.dumps(log_record)

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq.signalwave.svc.cluster.local')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'deploy')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'VMware123!')
QUEUE_NAME = os.getenv('RABBITMQ_QUEUE', 'signalwave')

rabbitmq_port_env = os.getenv('RABBITMQ_PORT', '5672')
if rabbitmq_port_env.startswith('tcp://'):
    RABBITMQ_PORT = int(urlparse(rabbitmq_port_env).port)
else:
    RABBITMQ_PORT = int(rabbitmq_port_env)

# HTML Template Path
HTML_TEMPLATE_PATH = "/usr/share/nginx/html/index.html"

# HTML Template Initialization
def initialize_html_template():
    """Initialize the HTML file with the basic structure."""
    logger.info("Initializing HTML template")
    try:
        with open(HTML_TEMPLATE_PATH, 'w') as file:
            file.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Observability Metrics</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f9; }
        header { background-color: #0073e6; color: white; padding: 1rem; text-align: center; font-size: 1.5rem; }
        footer { background-color: #333; color: white; text-align: center; padding: 1rem; position: fixed; bottom: 0; width: 100%; }
        .container { margin: 2rem auto; width: 90%; max-width: 800px; background: white; padding: 1rem; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); border-radius: 8px; }
        .metric { padding: 0.5rem; margin: 0.5rem 0; border-bottom: 1px solid #ddd; }
        .metric strong { font-size: 1.1rem; color: #333; }
    </style>
</head>
<body>
    <header>Network Observability Metrics</header>
    <div class="container" id="metric-container">
        <!-- Metrics will be appended here -->
    </div>
    <footer>&copy; 2025 Virtual Elephant Consulting Application. All rights reserved.</footer>
</body>
</html>
            """)

    except Exception as e:
        logger.error({"error": "Failed to initialize HTML template", "exception": str(e)})

# Initialize the HTML template
initialize_html_template()

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

try:
    # Establish connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments={"x-queue-type": "quorum"})
    logger.info("Successfully connected to RabbitMQ and declared queue")

    # Callback function to handle messages
    def callback(ch, method, properties, body):
        try:
            message = json.loads(body.decode())
            metrics = message.get("metrics", {})
            logger.info({"action": "consume", "metrics": metrics})

            # Append metrics to the HTML file
            metric_entries = "\n".join([
                f"""
                <div class="metric">
                    <strong>{key}</strong>: {value}
                </div>
                """
                for key, value in metrics.items()
            ])

            with open(HTML_TEMPLATE_PATH, 'r+') as file:
                content = file.read()
                insertion_point = content.find('<div class="container" id="metric-container">') + len('<div class="container" id="metric-container">')
                updated_content = content[:insertion_point] + metric_entries + content[insertion_point:]
                file.seek(0)
                file.write(updated_content)
                file.truncate()
                
        except json.JSONDecodeError as e:
            logger.error({"error": "Invalid JSON message", "body": body.decode(), "exception": str(e)})
        except Exception as e:
            logger.error({"error": "Failed to append log entry", "exception": str(e)})

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    logger.info("Starting to consume messages from RabbitMQ")
    channel.start_consuming()

except Exception as e:
    logger.error({"error": "Failed to connect or consume messages", "exception": str(e)})

finally:
    if 'connection' in locals() and connection.is_open:
        connection.close()
        logger.info("Connection to RabbitMQ closed")
