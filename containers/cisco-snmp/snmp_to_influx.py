from pysnmp.hlapi import (
    SnmpEngine, UsmUserData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity,
    usmHMACMD5AuthProtocol, usmDESPrivProtocol,
    nextCmd
)
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("snmp-monitor")

# SNMPv3 credentials
SNMP_USER = 'deploy'
AUTH_KEY = os.getenv("SNMP_AUTH_KEY")
PRIV_KEY = os.getenv("SNMP_PRIV_KEY")

# InfluxDB setup
INFLUX_URL = 'http://influxdb.home.virtualelephant.com'
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "monitoring")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG", "virtualelephant")
TARGET_FILE = os.getenv("TARGET_FILE", "/app/devices.txt")
INTERFACE_FILE = os.getenv("INTERFACE_FILE", "/app/interfaces.txt")

# Interface we care about
TARGET_INTERFACE_NAME = "Ethernet1/3"

# OIDs from IF-MIB
IFDESCR_OID       = '1.3.6.1.2.1.2.2.1.2'
IFINOCTETS_OID    = '1.3.6.1.2.1.2.2.1.10'
IFOUTOCTETS_OID   = '1.3.6.1.2.1.2.2.1.16'
IFINERRORS_OID    = '1.3.6.1.2.1.2.2.1.14'
IFOUTERRORS_OID   = '1.3.6.1.2.1.2.2.1.20'
IFINDISCARDS_OID  = '1.3.6.1.2.1.2.2.1.13'
IFOUTDISCARDS_OID = '1.3.6.1.2.1.2.2.1.19'

METRIC_OIDS = {
    IFINOCTETS_OID: "in_octets",
    IFOUTOCTETS_OID: "out_octets",
    IFINERRORS_OID: "in_errors",
    IFOUTERRORS_OID: "out_errors",
    IFINDISCARDS_OID: "in_discards",
    IFOUTDISCARDS_OID: "out_discards"
}

def load_devices():
    with open(TARGET_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def load_interfaces():
    with open(INTERFACE_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def snmp_walk(oid, target_ip):
    results = {}
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        UsmUserData(SNMP_USER, AUTH_KEY, PRIV_KEY,
                    authProtocol=usmHMACMD5AuthProtocol,
                    privProtocol=usmDESPrivProtocol),
        UdpTransportTarget((target_ip, 161), timeout=2, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    ):
        if errorIndication:
            logger.error(f"SNMP error on {target_ip}: {errorIndication}")
            break
        elif errorStatus:
            logger.warning(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            break
        else:
            for varBind in varBinds:
                oid_str, value = varBind
                index = int(str(oid_str).split('.')[-1])
                results[index] = str(value)
    return results

def collect_target_interface_stats(target_ip, target_interfaces):
    if_names = snmp_walk(IFDESCR_OID, target_ip)
    logger.info(f"{target_ip} - Interface names returned: {if_names}")

    # Correct: find index:name pairs for ALL target interfaces
    target_indices = {idx: name for idx, name in if_names.items() if name in target_interfaces}
    
    if not target_indices:
        logger.warning(f"{target_ip}: No matching interfaces found.")
        return []

    collected_stats = []
    for idx, interface_name in target_indices.items():
        stats = {"interface": interface_name}

        for oid, label in METRIC_OIDS.items():
            values = snmp_walk(oid, target_ip)
            logger.info(f"{target_ip} - SNMP walk for {label} ({oid}): {values}")

            value = values.get(idx, 0)
            try:
                stats[label] = int(value)
            except (ValueError, TypeError):
                try:
                    stats[label] = int.from_bytes(bytes(value), byteorder='big')
                except Exception as e:
                    stats[label] = 0
                    logger.warning(f"Failed to convert value '{value}' for {label} on {target_ip}: {e}")

        logger.info(f"{target_ip} - Final collected stats for {interface_name}: {stats}")
        collected_stats.append(stats)

    return collected_stats

def write_to_influx(target_ip, iface_data):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = Point("cisco_devices") \
        .tag("device", target_ip) \
        .tag("interface", iface_data["interface"])

    for key, value in iface_data.items():
        if key != "interface":
            point.field(key, value)

    point.time(time.time_ns(), WritePrecision.NS)

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    client.close()

if __name__ == "__main__":
    devices = load_devices()
    interfaces = load_interfaces()

    for ip in devices:
        logger.info(f"Collecting stats from {ip}")
        stats_list = collect_target_interface_stats(ip, interfaces)
        if stats_list:
            for iface_stats in stats_list:
                write_to_influx(ip, iface_stats)
            logger.info(f"Wrote {len(stats_list)} interface stats for {ip} to InfluxDB.")
        else:
            logger.warning(f"No stats collected for {ip}.")
