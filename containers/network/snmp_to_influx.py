from pysnmp.hlapi import (
    SnmpEngine, UsmUserData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity,
    usmHMACMD5AuthProtocol, usmDESPrivProtocol,
    nextCmd
)
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time

# SNMPv3 credentials
SNMP_USER = 'deploy'
AUTH_KEY = os.getenv("SNMP_AUTH_KEY")
PRIV_KEY = os.getenv("SNMP_PRIV_KEY")
TARGET_IP = '10.1.10.2'

# InfluxDB setup
INFLUX_URL = 'http://influxdb.home.virtualelephant.com'
INFLUX_TOKEN = 'nZHQrwn2ONAps6aCVCOtGx8OCdjfMIYfXU_iIOqsqyH4Ar0_SJNvPP9G4nswy-JhNvXvs74yKds5T5Rp1gmwsQ=='
ORG = 'virtualelephant'
BUCKET = 'monitoring'

def snmp_walk():
    results = []
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
            print(f"SNMP error: {errorIndication}")
            break
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            break
        else:
            for varBind in varBinds:
                results.append(varBind)
    return results

def write_to_influx(data):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for oid, value in data:
        point = Point("snmpwalk") \
            .tag("target", TARGET_IP) \
            .field(str(oid), str(value)) \
            .time(time.time_ns(), WritePrecision.NS)
        write_api.write(bucket=BUCKET, org=ORG, record=point)

    client.close()

if __name__ == "__main__":
    snmp_data = snmp_walk()
    if snmp_data:
        write_to_influx(snmp_data)
        print("SNMP data written to InfluxDB.")
    else:
        print("No SNMP data collected.")
