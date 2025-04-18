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
SWITCH_IPS = ['10.1.10.2', '10.1.10.3']

# InfluxDB setup
INFLUX_URL = 'http://influxdb.home.virtualelephant.com'
INFLUX_TOKEN = 'nZHQrwn2ONAps6aCVCOtGx8OCdjfMIYfXU_iIOqsqyH4Ar0_SJNvPP9G4nswy-JhNvXvs74yKds5T5Rp1gmwsQ=='
ORG = 'virtualelephant'
BUCKET = 'monitoring'

# OIDs from IF-MIB
IFDESCR_OID       = '1.3.6.1.2.1.2.2.1.2'
IFINOCTETS_OID    = '1.3.6.1.2.1.2.2.1.10'
IFOUTOCTETS_OID   = '1.3.6.1.2.1.2.2.1.16'
IFINERRORS_OID    = '1.3.6.1.2.1.2.2.1.14'
IFOUTERRORS_OID   = '1.3.6.1.2.1.2.2.1.20'
IFINDISCARDS_OID  = '1.3.6.1.2.1.2.2.1.13'
IFOUTDISCARDS_OID = '1.3.6.1.2.1.2.2.1.19'

# List of metric OIDs to collect
METRIC_OIDS = {
    IFINOCTETS_OID: "in_octets",
    IFOUTOCTETS_OID: "out_octets",
    IFINERRORS_OID: "in_errors",
    IFOUTERRORS_OID: "out_errors",
    IFINDISCARDS_OID: "in_discards",
    IFOUTDISCARDS_OID: "out_discards"
}

def snmp_walk(oid, target_ip):
    results = {}
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        UsmUserData(SNMP_USER, AUTH_KEY, PRIV_KEY,
                    authProtocol=usmHMACMD5AuthProtocol,
                    privProtocol=usmDESPrivProtocol),
        UdpTransportTarget((TARGET_IP, 161), timeout=2, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1')),  # Start of SNMP MIB tree
        lexicographicMode=False
    ):
        if errorIndication:
            logger.info(f"SNMP error: {errorIndication}")
            break
        elif errorStatus:
            logger.warning(f"{errorStatus.prettylogger.info()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            break
        else:
            for varBind in varBinds:
                oid_str, value = varBind
                index = int(str(oid_str).split('.')[-1])
                results[index] = str(value)
    return results

def collect_interface_stats(target_ip):
    if_names = snmp_walk(IFDESCR_OID, target_ip)
    stats_by_if = {idx: {"interface": if_names[idx]} for idx in if_names}

    for oid, label in METRIC_OIDS.items():
        values = snmp_walk(oid, target_ip)
        for idx, val in values.items():
            if idx in stats_by_if:
                stats_by_if[idx][label] = int(val)

    return list(stats_by_if.values())

def write_to_influx(target_ip,data):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for iface in data:
        point = Point("interface_stats") \
            .tag("device", target_ip) \
            .tag("interface", iface.get("interface", "unknown"))

        for key, value in iface.items():
            if key != "interface":
                point.field(key, value)

        point.time(time.time_ns(), WritePrecision.NS)
        write_api.write(bucket=BUCKET, org=ORG, record=point)

    client.close()

if __name__ == "__main__":
    for ip in SWITCH_IPS:
        logger.info(f"Collecting stats from {ip}")
        stats = collect_interface_stats(ip)
        if stats:
            write_to_influx(stats)
            logger.info(f"Wrote {len(stats)} interface stats for {ip} to InfluxDB.")
        else:
            logger.warning("No interface data collected from {ip}.")
