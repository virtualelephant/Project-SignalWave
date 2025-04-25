import subprocess
import datetime
import requests
import time
import os

INFLUX_URL = os.getenv("INFLUX_URL", "http://influxdb.home.virtualelephant.com:8086")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "ping")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG", "virtualelephant")
TARGET_FILE = os.getenv("TARGET_FILE", "/app/targets.txt")

def load_targets():
    with open(TARGET_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def ping_targets(targets):
    result = subprocess.run(["fping", "-C", "5", "-q"] + targets,
                            capture_output=True, text=True)
    lines = result.stderr.strip().split('\n')
    timestamp = int(time.time() * 1e9)  # nanoseconds
    payload = ""

    for line in lines:
        parts = line.split(":")
        target = parts[0].strip()
        stats = parts[1].strip().split()
        stats = [s if s != "-" else "NaN" for s in stats]
        numeric_stats = [float(x) for x in stats if x != "NaN"]
        sent = len(stats)
        recv = len(numeric_stats)
        loss = round(100 * (sent - recv) / sent, 2) if sent > 0 else 0
        avg = sum(numeric_stats) / recv if recv > 0 else 0
        min_val = min(numeric_stats) if recv > 0 else 0
        max_val = max(numeric_stats) if recv > 0 else 0

        payload += f"ping,target={target} sent={sent}i,recv={recv}i,loss={loss},min={min_val},avg={avg},max={max_val} {timestamp}\n"

    return payload

def write_to_influx(data):
    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain; charset=utf-8"
    }
    url = f"{INFLUX_URL}/api/v2/write?org={INFLUX_ORG}&bucket={INFLUX_BUCKET}&precision=ns"
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()

if __name__ == "__main__":
    try:
        targets = load_targets()
        data = ping_targets(targets)
        write_to_influx(data)
        print("Data successfully written to InfluxDB.")
    except Exception as e:
        print(f"Error: {e}")
