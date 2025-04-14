import os
import json
import logging
import datetime
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- Logging (stdout for Fluentd) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants & Environment ---
API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")
INFLUX_URL = os.getenv("INFLUXDB_URL", "http://influxdb.monitoring.svc.cluster.local:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG", "weather-org")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET", "weather")

# --- Load city list ---
def load_cities(file_path="/app/cities.txt"):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

# --- Connect to InfluxDB ---
def connect_to_influxdb():
    client = InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG
    )
    return client, client.query_api(), client.write_api(write_options=SYNCHRONOUS)

# --- Check if city/date exists ---
def record_exists(query_api, city, date):
    flux = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {date}T00:00:00Z, stop: {date}T23:59:59Z)
      |> filter(fn: (r) => r._measurement == "weather" and r.city == "{city}" and r.type == "daily-history")
      |> limit(n:1)
    '''
    try:
        result = query_api.query(flux)
        return len(result) > 0
    except Exception as e:
        logger.warning(f"InfluxDB query error for {city} on {date}: {e}")
        return False

# --- Fetch weather data ---
def fetch_weather_data(city, start_date, end_date):
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{city}/{start_date}/{end_date}?unitGroup=us&key={API_KEY}&contentType=json"
    )
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Failed to fetch data for {city}: {response.status_code} {response.text}")
        return []
    return response.json().get("days", [])

# --- Main ---
def main():
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=365)
    end_date = today

    cities = load_cities()
    client, query_api, write_api = connect_to_influxdb()

    for city in cities:
        logger.info(f"Fetching data for city: {city}")
        weather_data = fetch_weather_data(city, start_date, end_date)

        for entry in weather_data:
            date = entry["datetime"]
            if record_exists(query_api, city, date):
                logger.debug(f"Already in InfluxDB: {city} {date}")
                continue

            point = (
                Point("weather")
                .tag("city", city)
                .tag("type", "daily-history")
                .field("temperature_high", entry["tempmax"])
                .field("temperature_low", entry["tempmin"])
                .time(f"{date}T00:00:00Z")
            )

            try:
                write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
                logger.info(f"Wrote to InfluxDB: {city} {date}")
            except Exception as e:
                logger.error(f"Write failed for {city} {date}: {e}")

    client.close()

if __name__ == "__main__":
    main()
