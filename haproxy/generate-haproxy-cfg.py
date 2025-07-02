#!/usr/bin/env python3

import subprocess
import hashlib
import os

CONFIG_PATH = "/etc/haproxy/haproxy.cfg"
TMP_PATH = "/home/deploy/haproxy/haproxy.cfg.tmp"

KUBECONFIG_PATH = "/home/deploy/haproxy/kubeconfig"

VIP_API = "10.5.1.13"
VIP_APPS = "10.5.1.12"
INGRESS_SVC = "rk2-ingress-nginx-controller-admission"
INGRESS_NS = "kube-system"
KUBE_API_PORT = 6443
APP_PORT = 80  # Change to 443 for SSL frontend

def get_endpoints(service_name, namespace):
    try:
        result = subprocess.check_output([
            "kubectl", "--kubeconfig", KUBECONFIG_PATH, "get", "endpoints", service_name, "-n", namespace,
            "-o", "jsonpath={.subsets[*].addresses[*].ip}"
        ])
        return result.decode("utf-8").split()
    except subprocess.CalledProcessError as e:
        print(f"Failed to fetch endpoints for {service_name}: {e}")
        return []

def generate_haproxy_config():
    kube_api_endpoints = get_endpoints("kubernetes", "default")
    app_endpoints = get_endpoints(INGRESS_SVC, INGRESS_NS)

    with open(TMP_PATH, "w") as f:
        f.write("global\n")
        f.write("    log /dev/log local0\n")
        f.write("    maxconn 2000\n")
        f.write("    daemon\n\n")

        f.write("defaults\n")
        f.write("    log     global\n")
        f.write("    mode    tcp\n")
        f.write("    timeout connect 5s\n")
        f.write("    timeout client  50s\n")
        f.write("    timeout server  50s\n\n")

        # Kubernetes API Frontend + Backend
        f.write("frontend kubernetes_api\n")
        f.write(f"    bind {VIP_API}:{KUBE_API_PORT}\n")
        f.write("    mode tcp\n")
        f.write("    default_backend kube_api_backends\n\n")

        f.write("backend kube_api_backends\n")
        f.write("    mode tcp\n")
        f.write("    option ssl-hello-chk\n")
        for idx, ip in enumerate(kube_api_endpoints):
            f.write(f"    server k8s-{idx} {ip}:{KUBE_API_PORT} check\n")
        f.write("\n")

        # HTTP Frontend + Backend
        f.write("frontend http_apps\n")
        f.write(f"    bind {VIP_APPS}:80\n")
        f.write("    mode http\n")
        f.write("    default_backend app_http_backends\n\n")

        f.write("backend app_http_backends\n")
        f.write("    mode http\n")
        f.write("    balance roundrobin\n")
        f.write("    option httpchk GET /\n")
        for idx, ip in enumerate(app_endpoints):
            f.write(f"    server app-http-{idx} {ip}:80 check\n")
        f.write("\n")

        # HTTPS Frontend + Backend (optional)
        f.write("frontend https_apps\n")
        f.write(f"    bind {VIP_APPS}:443 ssl crt /etc/haproxy/certs/app_bundle.pem\n")
        f.write("    mode http\n")
        f.write("    default_backend app_https_backends\n\n")

        f.write("backend app_https_backends\n")
        f.write("    mode http\n")
        f.write("    balance roundrobin\n")
        f.write("    option httpchk GET /\n")
        for idx, ip in enumerate(app_endpoints):
            f.write(f"    server app-https-{idx} {ip}:443 check ssl verify none\n")

def config_changed():
    if not os.path.exists(CONFIG_PATH):
        return True

    with open(CONFIG_PATH, "rb") as f1, open(TMP_PATH, "rb") as f2:
        return hashlib.md5(f1.read()).digest() != hashlib.md5(f2.read()).digest()

def reload_haproxy():
    subprocess.run(["systemctl", "reload", "haproxy"], check=False)

if __name__ == "__main__":
    generate_haproxy_config()
    if config_changed():
        os.replace(TMP_PATH, CONFIG_PATH)
        print("Updated HAProxy config. Reloading...")
        reload_haproxy()
    else:
        print("No config change. Skipping reload.")
