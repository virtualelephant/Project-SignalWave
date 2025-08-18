import time
import psutil
import logging
import yaml
import socket
from influxdb_client import InfluxDBClient, Point, WriteOptions

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

INFLUXDB_URL = config["influxdb"]["url"]
INFLUXDB_TOKEN = config["influxdb"]["token"]
INFLUXDB_ORG = config["influxdb"]["org"]
INFLUXDB_BUCKET = config["influxdb"]["bucket"]
POLL_INTERVAL_SECONDS = config["poll_interval_minutes"] * 60

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

hostname = socket.gethostname()

# Connect to InfluxDB
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=WriteOptions(batch_size=500, flush_interval=10_000))

def collect_metrics():
    # CPU
    cpu_percent_total = psutil.cpu_percent(interval=1)
    cpu_per_core = psutil.cpu_percent(percpu=True)
    load_avg_1, load_avg_5, load_avg_15 = psutil.getloadavg()

    # Memory
    mem = psutil.virtual_memory()
    
    # Disk
    disk = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()

    # Network
    net = psutil.net_io_counters()

    point = (
        Point("system_metrics")
        .tag("host", hostname)
        # CPU Metrics
        .field("cpu_percent_total", cpu_percent_total)
        .field("load_avg_1m", load_avg_1)
        .field("load_avg_5m", load_avg_5)
        .field("load_avg_15m", load_avg_15)
        # Memory Metrics
        .field("memory_percent", mem.percent)
        .field("memory_total_mb", mem.total / 1024 / 1024)
        .field("memory_used_mb", mem.used / 1024 / 1024)
        .field("memory_free_mb", mem.free / 1024 / 1024)
        .field("memory_cached_mb", mem.cached / 1024 / 1024)
        # Disk Metrics
        .field("disk_usage_percent", disk.percent)
        .field("disk_total_gb", disk.total / 1024 / 1024 / 1024)
        .field("disk_used_gb", disk.used / 1024 / 1024 / 1024)
        .field("disk_free_gb", disk.free / 1024 / 1024 / 1024)
        .field("disk_read_bytes", disk_io.read_bytes)
        .field("disk_write_bytes", disk_io.write_bytes)
        # Network Metrics
        .field("network_bytes_sent", net.bytes_sent)
        .field("network_bytes_recv", net.bytes_recv)
        .field("network_packets_sent", net.packets_sent)
        .field("network_packets_recv", net.packets_recv)
        .field("network_errin", net.errin)
        .field("network_errout", net.errout)
    )

    # Add per-core CPU utilization
    for i, percent in enumerate(cpu_per_core):
        point.field(f"cpu_core_{i}_percent", percent)

    return [point]

def main():
    logging.info("Starting metrics collector... Polling every %d minutes.", config["poll_interval_minutes"])
    while True:
        try:
            points = collect_metrics()
            write_api.write(bucket=INFLUXDB_BUCKET, record=points)
            logging.info("Metrics pushed to InfluxDB successfully.")
        except Exception as e:
            logging.error("Error while collecting/sending metrics: %s", str(e))
        
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
