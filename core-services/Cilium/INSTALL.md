# Installing Cilium CNI inside Kubenetes Cluster

## Installing the Cilium CLI

```bash
CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
CLI_ARCH=amd64
if [ "$(uname -m)" = "aarch64" ]; then CLI_ARCH=arm64; fi
curl -L --fail --remote-name-all https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
sha256sum --check cilium-linux-${CLI_ARCH}.tar.gz.sha256sum
sudo tar xzvfC cilium-linux-${CLI_ARCH}.tar.gz /usr/local/bin
rm cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
```

## Installing Cilium using the Helm Repo
```bash
helm repo add cilium https://helm.cilium.io
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.0/standard-install.yaml
helm install cilium cilium/cilium --version 1.18.2 \
    --namespace kube-system \
    --set hubble.enabled=true \
    --set hubble.metrics.enableOpenMetrics=true \
    --set hubble.metrics.enabled="{dns,drop,tcp,flow,port-distribution,icmp,httpV2:exemplars=true;labelsContext=source_ip\,source_namespace\,source_workload\,destination_ip\,destination_namespace\,destination_workload\,traffic_direction}" \
    --set hubble.relay.enabled=true \
    --set hubble.ui.enabled=true \
    --set prometheus.enabled=true \
    --set prometheus.operator.enabled=true \
    --set bgpControlPlane.enabled=true \
    --set installCRDs=true \
    --set gatewayAPI.enabled=true \
    --set gatewayAPI.gatewayClass.create="true"
```

## Configuring BGP
```bash
kubectl apply -f k8s/manifests/cilium/bgp/01_lb_pool.yaml
kubectl apply -f k8s/manifests/cilium/bgp/02_bgp_advertisements.yaml
kubectl apply -f k8s/manifests/cilium/bgp/03_bgp_peer_config.yaml
kubectl apply -f k8s/manifests/cilium/bgp/04_bgp_cluster_config.yaml
```

There is a smoke-test to validate the BGP and IP Pool settings are properly setup and being advertised across the network
```bash
kubectl apply -f k8s/manifests/cilium/bgp/99_smoke_test.yaml
```

## Creating Gateway API for Hubble UI
```bash
kubectl apply -f k8s/manifests/cilium/hubble/00_gateway_class.yaml
kubectl apply -f k8s/manifests/cilium/hubble/01_hubble_gateway.yaml
kubectl apply -f k8s/manifests/cilium/hubble/02_hubble_route.yaml
```
