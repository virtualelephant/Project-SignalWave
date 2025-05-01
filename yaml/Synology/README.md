# Synology SNMPv3 Monitoring Application
This document provides installation instructions for running the application inside a Kubernetes environment to monitory, via SNMPv3, a set of Synology arrays as defined in a target file. The application runs inside the `monitoring` namespace as a deployment.

This document also provides a complete list of SNMPv3 OIDs used to monitor Synology NAS devices, along with equivalent `snmpget` and `snmpwalk` CLI commands to validate and debug data collection, that can be used to validate the Synology targets and DSM version are compatible with the Python script leveraged inside the container.

---
# Installation Commands
Be sure you have already created the container and uploaded it to a local container registry. If you have not yet created the container, please perform the following commands:

```bash
cd containers/synology-snmp
docker build -t --no-cache YOUR.REPO/LIBRARY/synology-snmp:latest .
docker push YOUR.REPO/LIBRARY/synology-snmp:latest
```

Modify the `synology-snmp-deployment.yaml` to point to your container registry before deploying into the Kubernetes cluster.

```bash
kubectl apply -f yaml/Synology/synology-snmp-deployment.yaml
```

---
# DEBUG Commands
All commands assume SNMPv3 with MD5 (auth) and AES (priv), using the `authPriv` security level.

## SNMPv3 Connection Format

```bash
snmpwalk -v3 -l authPriv \
  -u <username> \
  -a MD5 -A <auth_pass> \
  -x AES -X <priv_pass> \
  <target_ip> <OID>
```

## SNMPv3 Commands

Run these commands to validate the SNMP OIDs for the target Synology array are compatible with the target hardware and DSM version. Assumes you have already configured SNMPv3 on the Synology array itself and created the necessary MD5 privileged username and password, as well as the AES privileged password.

```bash
snmpget -v3 -l authPriv -u <user> -a MD5 -A <authpass> -x AES -X <privpass> <ip> 1.3.6.1.4.1.6574.1.1.0
snmpget -v3 -l authPriv -u <user> -a MD5 -A <authpass> -x AES -X <privpass> <ip> 1.3.6.1.4.1.6574.1.2.0
snmpget -v3 -l authPriv -u <user> -a MD5 -A <authpass> -x AES -X <privpass> <ip> 1.3.6.1.4.1.6574.1.5.1.0

snmpwalk -v3 -l authPriv -u <user> -a MD5 -A <authpass> -x AES -X <privpass> <ip> 1.3.6.1.4.1.6574.2.1.1.3
snmpwalk -v3 -l authPriv -u <user> -a MD5 -A <authpass> -x AES -X <privpass> <ip> 1.3.6.1.4.1.6574.2.1.1.5
snmpwalk -v3 -l authPriv -u <user> -a MD5 -A <authpass> -x AES -X <privpass> <ip> 1.3.6.1.4.1.6574.2.1.1.6

snmpwalk -v3 -l authPriv -u <user> -a MD5 -A <authpass> -x AES -X <privpass> <ip> 1.3.6.1.4.1.6574.2.1.1.2
snmpwalk -v3 -l authPriv -u <user> -a MD5 -A <authpass> -x AES -X <privpass> <ip> 1.3.6.1.4.1.6574.2.1.1.6

snmpwalk -v3 -l authPriv -u <user> -a MD5 -A <authpass> -x AES -X <privpass> <ip> 1.3.6.1.4.1.6574
```