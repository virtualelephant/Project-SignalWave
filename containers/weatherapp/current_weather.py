import os
import json
import logging
import datetime
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from time import sleep

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants & Env Vars ---
INFLUX_URL = os.getenv("INFLUXDB_URL", "http://influxdb.monitoring.svc.cluster.local:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG", "virtualelephant")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET", "weather")

GEOCODE_URL = "https://nominatim.openstreetmap.org/search"

# --- Load cities ---
def load_cities(file_path="/app/cities.txt"):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

# --- Get coordinates from city name ---
def get_coordinates(city):
    try:
        params = {"q": city, "format": "json", "limit": 1}
        headers = {"User-Agent": "WeatherDataCollector/1.0"}
        response = requests.get(GEOCODE_URL, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()
        if not results:
            logger.warning(f"No coordinates found for city: {city}")
            return None, None
        lat = results[0]["lat"]
        lon = results[0]["lon"]
        return lat, lon
    except Exception as e:
        logger.error(f"Geocoding failed for {city}: {e}")
        return None, None

def c_to_f(celsius):
    return (celsius * 9/5) + 32

# --- Fetch current weather from Open-Meteo ---
def fetch_current_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&current_weather=true"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("current_weather", {})
    except Exception as e:
        logger.error(f"Failed to fetch current weather for {lat}, {lon}: {e}")
        return None

# --- Main ---
def main():
    cities = load_cities()
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for city in cities:
        logger.info(f"Processing city: {city}")
        lat, lon = get_coordinates(city)
        if not lat or not lon:
            continue

        data = fetch_current_weather(lat, lon)
        if not data or "temperature" not in data:
            logger.warning(f"No current temperature returned for {city}")
            continue

        now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        point = (
            Point("weather")
            .tag("city", city)
            .tag("type", "current")
            .field("temperature_current", c_to_f(data["temperature"]))
            .time(now)
        )

        try:
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            logger.info(f"Wrote current temp for {city} at {now}: {c_to_f(data['temperature'])}°F")
        except Exception as e:
            logger.error(f"Failed to write current temp for {city}: {e}")

        sleep(1)  # Be polite to OpenStreetMap/Open-Meteo

    client.close()

if __name__ == "__main__":
    main()
