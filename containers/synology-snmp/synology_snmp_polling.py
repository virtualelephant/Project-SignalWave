from pysnmp.hlapi import (
    SnmpEngine, UsmUserData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity,
    usmHMACMD5AuthProtocol, usmAesCfb128Protocol,
    nextCmd, getCmd
)
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time
import datetime
import logging

# ---------------------------
# Logging Setup
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("synology-monitor")

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

TARGET_FILE = os.getenv("TARGET_FILE", "/app/synology_targets.txt")

# ---------------------------
# SNMP Helper Functions
# ---------------------------
def snmp_get(oid, ip):
    errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(
        SnmpEngine(),
        UsmUserData(SNMP_USER, AUTH_KEY, PRIV_KEY,
                    authProtocol=usmHMACMD5AuthProtocol,
                    privProtocol=usmAesCfb128Protocol),
        UdpTransportTarget((ip, 161), timeout=2, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    ))
    if errorIndication:
        logger.error(f"{ip} SNMP error: {errorIndication}")
        return None
    elif errorStatus:
        logger.warning(f"{ip} SNMP get failed: {errorStatus.prettyPrint()}")
        return None
    else:
        return str(varBinds[0][1])

def snmp_walk(oid, ip):
    result = {}
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        UsmUserData(SNMP_USER, AUTH_KEY, PRIV_KEY,
                    authProtocol=usmHMACMD5AuthProtocol,
                    privProtocol=usmAesCfb128Protocol),
        UdpTransportTarget((ip, 161), timeout=2, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    ):
        if errorIndication:
            logger.error(f"{ip} SNMP error: {errorIndication}")
            break
        elif errorStatus:
            logger.warning(f"{ip} SNMP walk failed: {errorStatus.prettyPrint()}")
            break
        else:
            for varBind in varBinds:
                oid_str, val = varBind
                index = str(oid_str).split('.')[-1]
                result[index] = str(val)
    return result

# ---------------------------
# InfluxDB Write
# ---------------------------
def write_synology_metrics(ip, metrics, timestamp, influx):
    for measurement, data in metrics.items():
        point = Point(measurement).tag("device", ip)
        for key, val in data.items():
            try:
                point.field(key, float(val))
            except ValueError:
                point.field(key, val)
        point.time(timestamp, WritePrecision.S)
        influx.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

# ---------------------------
# Polling Logic
# ---------------------------
def collect_synology_metrics(ip):
    timestamp = datetime.datetime.utcnow()

    # System info
    system_status = snmp_get('1.3.6.1.4.1.6574.1.1.0', ip)      # 1 = Normal
    temperature = snmp_get('1.3.6.1.4.1.6574.1.2.0', ip)        # Degrees C
    dsm_version = snmp_get('1.3.6.1.4.1.6574.1.5.1.0', ip)

    # Volumes
    volume_status = snmp_walk('1.3.6.1.4.1.6574.2.1.1.6', ip)   # volume status
    volume_size = snmp_walk('1.3.6.1.4.1.6574.2.1.1.5', ip)     # volume size MB
    volume_used = snmp_walk('1.3.6.1.4.1.6574.2.1.1.3', ip)     # used MB

    # Disks
    disk_status = snmp_walk('1.3.6.1.4.1.6574.2.1.1.2', ip)
    disk_temp = snmp_walk('1.3.6.1.4.1.6574.2.1.1.6', ip)

    metrics = {
        "synology_system": {
            "system_status": system_status,
            "temperature_c": temperature,
            "dsm_version": dsm_version
        }
    }

    for idx in volume_status:
        metrics[f"synology_volume_{idx}"] = {
            "status": volume_status.get(idx, "N/A"),
            "size_mb": volume_size.get(idx, 0),
            "used_mb": volume_used.get(idx, 0),
        }

    for idx in disk_status:
        metrics[f"synology_disk_{idx}"] = {
            "status": disk_status.get(idx, "N/A"),
            "temperature_c": disk_temp.get(idx, 0),
        }

    return metrics, timestamp

# ---------------------------
# Main Polling Daemon Loop
# ---------------------------
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))  # default: 300s

def main():
    with open(TARGET_FILE) as f:
        targets = [line.strip() for line in f if line.strip()]

    logger.info("Starting Synology SNMP Monitor Daemon...")

    while True:
        try:
            now = datetime.datetime.utcnow()

            # Reconnect to InfluxDB each cycle for robustness
            influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG).write_api(write_options=SYNCHRONOUS)

            for ip in targets:
                start_time = time.time()
                logger.info(f"Polling Synology metrics from {ip}")

                try:
                    metrics, ts = collect_synology_metrics(ip)
                    write_synology_metrics(ip, metrics, ts, influx)
                    logger.info(f"Wrote metrics for {ip} to InfluxDB.")
                except Exception as inner:
                    logger.error(f"Failed to collect/write metrics for {ip}: {inner}")

                duration = time.time() - start_time
                logger.info(f"Polling {ip} completed in {duration:.2f} seconds.")

        except Exception as e:
            logger.error(f"Polling cycle failed: {e}")

        logger.info(f"Sleeping for {POLL_INTERVAL} seconds...")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()

