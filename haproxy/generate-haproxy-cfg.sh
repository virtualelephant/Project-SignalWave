#!/bin/bash

# Configuration
SERVICE_NAME=ingress-nginx-controller
NAMESPACE=ingress-nginx
PORT=80
CONFIG_FILE=/etc/haproxy/haproxy.cfg
TMP_CONFIG=/tmp/haproxy.cfg.tmp
VIP_IP=10.5.1.13

# Generate new HAProxy config
cat <<EOF > $TMP_CONFIG
global
    log /dev/log    local0
    maxconn 2000
    daemon

defaults
    log     global
    mode    http
    option  httplog
    timeout connect 5s
    timeout client  50s
    timeout server  50s

frontend http_front
    bind ${VIP_IP}:80
    mode http
    default_backend nginx_backend

backend nginx_backend
    balance roundrobin
    option httpchk GET /
EOF

# Fetch IPs of service endpoints
ENDPOINTS=$(kubectl get endpoints $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}')

for IP in $ENDPOINTS; do
    echo "    server srv-${IP} ${IP}:${PORT} check" >> $TMP_CONFIG
done

# Replace live config if it has changed
if ! cmp -s "$TMP_CONFIG" "$CONFIG_FILE"; then
    mv $TMP_CONFIG $CONFIG_FILE
    systemctl reload haproxy
    echo "HAProxy config updated and reloaded."
else
    echo "No changes to HAProxy config."
fi
