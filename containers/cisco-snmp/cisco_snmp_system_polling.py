from pysnmp.hlapi import (
    SnmpEngine, UsmUserData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity,
    usmHMACMD5AuthProtocol, usmDESPrivProtocol,
    nextCmd, getCmd
)
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import os
import logging
import datetime

# ---------------------------
# Logging Setup
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("snmp-system-monitor")

# ---------------------------
# Environment Variables
# ---------------------------
SNMP_USER = 'deploy'
AUTH_KEY = os.getenv("SNMP_AUTH_KEY")
PRIV_KEY = os.getenv("SNMP_PRIV_KEY")

INFLUX_URL = 'http://influxdb.home.virtualelephant.com'
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "monitoring")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG", "virtualelephant")

TARGET_FILE = os.getenv("TARGET_FILE", "/app/system_devices.txt")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))  # default 5 min

# ---------------------------
# OIDs for System Stats
# ---------------------------
CPU_LOAD_OID = '1.3.6.1.4.1.9.9.305.1.1.1.0'
MEMORY_USAGE_OID = '1.3.6.1.4.1.9.9.305.1.1.2.0'

# ---------------------------
# Helper Functions
# ---------------------------
def load_devices():
    with open(TARGET_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def round_time_to_interval(now, interval_seconds=300):
    discard = datetime.timedelta(seconds=now.second % interval_seconds, microseconds=now.microsecond)
    return now - discard

def snmp_get(oid, target_ip):
    """Simple SNMPv3 GET"""
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(
            SnmpEngine(),
            UsmUserData(SNMP_USER, AUTH_KEY, PRIV_KEY,
                        authProtocol=usmHMACMD5AuthProtocol,
                        privProtocol=usmDESPrivProtocol),
            UdpTransportTarget((target_ip, 161), timeout=2, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
    )

    if errorIndication:
        logger.error(f"SNMP GET error on {target_ip}: {errorIndication}")
        return None
    elif errorStatus:
        logger.warning(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex)-1][0] or '?'}")
        return None
    else:
        for varBind in varBinds:
            oid_str, value = varBind
            return str(value)
    return None

def collect_system_stats(target_ip):
    stats = {}
    stats["cpu_load_percent"] = snmp_get(CPU_LOAD_OID, target_ip)
    stats["memory_usage_percent"] = snmp_get(MEMORY_USAGE_OID, target_ip)
    return stats

def write_system_metrics(target_ip, system_data, timestamp):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = Point("cisco_system_metrics") \
        .tag("device", target_ip)

    for key, value in system_data.items():
        if value is not None:
            try:
                point.field(key, float(value))
            except ValueError:
                logger.warning(f"Could not convert {key}='{value}' to float for {target_ip}")

    point.time(timestamp, WritePrecision.S)
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    client.close()

# ---------------------------
# Main Polling Loop
# ---------------------------
if __name__ == "__main__":
    devices = load_devices()

    logger.info("Starting Cisco System SNMP Monitor...")

    while True:
        try:
            now = datetime.datetime.utcnow()
            rounded_time = round_time_to_interval(now)

            for ip in devices:
                logger.info(f"Collecting system stats from {ip}")
                system_data = collect_system_stats(ip)
                write_system_metrics(ip, system_data, timestamp=rounded_time)
                logger.info(f"Wrote system stats for {ip} to InfluxDB.")

        except Exception as e:
            logger.error(f"Polling cycle failed: {e}")

        logger.info(f"Sleeping for {POLL_INTERVAL} seconds...")
        time.sleep(POLL_INTERVAL)
