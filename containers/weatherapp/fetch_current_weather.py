import os
import json
import logging
import datetime
import requests
import pika

# Setup logging
logging.basicConfig(
    filename='current_weather.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

RABBITMQ_HOST = "rabbitmq.monitoring.svc.cluster.local"
RABBITMQ_QUEUE = "weather"
API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")

def load_cities(file_path="/app/cities.txt"):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def connect_to_rabbitmq():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    return connection, channel

def fetch_current_temp(city):
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{city}/today?unitGroup=us&key={API_KEY}&include=current&contentType=json"
    )
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch current temp for {city}: {response.text}")
        return None
    return response.json().get("currentConditions", {})

def main():
    cities = load_cities()
    connection, channel = connect_to_rabbitmq()

    for city in cities:
        data = fetch_current_temp(city)
        if not data:
            continue

        payload = {
            "city": city,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "temperature_current": data.get("temp"),
            "type": "current"
        }

        message = json.dumps(payload)
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logging.info(f"Published current temp: {message}")

    connection.close()

if __name__ == "__main__":
    main()
