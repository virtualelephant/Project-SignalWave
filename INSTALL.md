# Installation Guide
## Current Version: v1.0
## Last Modified: 01.January.2025
## Maintainer: chris@virtualelephant.com

## Installing NFS Client Provisioner
https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner

```
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
    --set nfs.server=x.x.x.x \
    --set nfs.path=/exported/path \
    --create-namespace \
    --namespace=nfs-storage
```

In the `yaml/SignalWave` directory, modify the `storageclass.yaml` file to point to the NFS server and apply it in the cluster.
```
kubectl apply -f storageclass.yaml
```

## Installing HAProxy Ingress Controller
```
helm repo add haproxytech https://haproxytech.github.io/helm-charts
helm install haproxy-kubernetes-ingress haproxytech/kubernetes-ingress --create-namespace --namespace haproxy
```

## Installing Grafana and Prometheus
Modify the `yaml/Cilium/monitoring.yaml` file, editing lines 14289 & 14290 to reflect the NFS server in the environment.
```
kubectl apply -f yaml/Cilium/monitoring.yaml -n cilium-monitoring
kubectl apply -f yaml/Cilium/monitoring-ingress.yaml -n cilium-monitoring
```

## Create SignalWave Namespace
```
kubectl create namespace signalwave
```

## Installing RabbitMQ Operator
https://www.rabbitmq.com/kubernetes/operator/quickstart-operator.html

```
kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"
```

Build the local RabbitMQ application in the Kubernetes environment:
```
kubectl apply -f yaml/SignalWave/rabbitmq-prod.yaml -n signalwave
kubectl apply -f yaml/SignalWave/rabbitmq-ingress.yaml -n signalwave
```