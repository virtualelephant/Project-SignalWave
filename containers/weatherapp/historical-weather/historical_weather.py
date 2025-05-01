import os
import json
import logging
import datetime
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from time import sleep

# --- Logging (stdout for Fluentd) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants & Env Vars ---
INFLUX_URL = os.getenv("INFLUXDB_URL", "http://influxdb.monitoring.svc.cluster.local:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG", "virtualelephant")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET", "monitoring")

GEOCODE_URL = "https://nominatim.openstreetmap.org/search"

# --- Load cities ---
def load_cities(file_path="/app/cities.txt"):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

# --- Get coordinates for a city (lat, lon) ---
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
    if celsius is None:
        return None
    return (celsius * 9/5) + 32

# --- Connect to InfluxDB ---
def connect_to_influxdb():
    client = InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG
    )
    return client, client.query_api(), client.write_api(write_options=SYNCHRONOUS)

# --- Check if record already exists in InfluxDB ---
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
        logger.warning(f"InfluxDB query failed for {city} {date}: {e}")
        return False

# --- Fetch weather data from Open-Meteo archive API ---
def fetch_weather_data(lat, lon, start_date, end_date):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&daily=temperature_2m_max,temperature_2m_min"
        f"&timezone=auto"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Weather data fetch failed for {lat}, {lon}: {e}")
        return None

# --- Main ---
def main():
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=30)
    end_date = today

    cities = load_cities()
    client, query_api, write_api = connect_to_influxdb()

    for city in cities:
        logger.info(f"Processing city: {city}")
        lat, lon = get_coordinates(city)
        if not lat or not lon:
            continue

        data = fetch_weather_data(lat, lon, start_date, end_date)
        if not data or "daily" not in data:
            logger.warning(f"No data returned for {city}")
            continue

        dates = data["daily"]["time"]
        highs = data["daily"]["temperature_2m_max"]
        lows = data["daily"]["temperature_2m_min"]

        for i in range(len(dates)):
            date = dates[i]
            high = highs[i]
            low = lows[i]

            if record_exists(query_api, city, date):
                logger.debug(f"Record already exists: {city} {date}")
                continue

            point = (
                Point("weather")
                .tag("city", city)
                .tag("type", "daily-history")
                .field("temperature_high", c_to_f(high))
                .field("temperature_low", c_to_f(low))
                .time(f"{date}T00:00:00Z")
            )

            try:
                write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
                logger.info(f"Wrote data for {city} on {date}")
            except Exception as e:
                logger.error(f"Failed to write InfluxDB point for {city} {date}: {e}")

        # Be polite to the geocoding and Open-Meteo APIs
        sleep(1)

    client.close()

if __name__ == "__main__":
    main()
