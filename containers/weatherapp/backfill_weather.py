import os
import json
import logging
import datetime
import requests
import pika

# Setup logging
logging.basicConfig(
    filename='weather_backfill.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Constants
RABBITMQ_HOST = "rabbitmq.monitoring.svc.cluster.local"
RABBITMQ_QUEUE = "weather"
API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")
CITIES = os.getenv("CITY_LIST", "Austin,TX").split(";")

# Read cities from /app/cities.txt
def load_cities(file_path="/app/cities.txt"):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

CITIES = load_cities()


# Setup RabbitMQ connection
def connect_to_rabbitmq():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    return connection, channel

# Fetch weather history for a given city
def fetch_weather_data(city, start_date, end_date):
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{city}/{start_date}/{end_date}?unitGroup=us&key={API_KEY}&contentType=json"
    )
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch data for {city}: {response.text}")
        return []
    return response.json().get("days", [])

# Main process
def main():
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=365)
    end_date = today

    connection, channel = connect_to_rabbitmq()

    for city in CITIES:
        logging.info(f"Processing city: {city}")
        weather_data = fetch_weather_data(city, start_date, end_date)
        
        for entry in weather_data:
            payload = {
                "city": city,
                "date": entry["datetime"],
                "temperature_high": entry["tempmax"],
                "temperature_low": entry["tempmin"],
                "type": "daily-history"
            }

            message = json.dumps(payload)
            # Send to RabbitMQ
            channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_QUEUE,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)  # persistent
            )

            # Log message to file
            logging.info(f"Published: {message}")

    connection.close()

if __name__ == "__main__":
    main()
