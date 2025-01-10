# Installation Guide
- Current Version: v1.0
- Last Modified: 02.January.2025
- Maintainer: chris@virtualelephant.com

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
kubectl apply -f storageclass-retain.yaml
```

## Installing HAProxy Ingress Controller
```
helm repo add haproxytech https://haproxytech.github.io/helm-charts
helm install haproxy-kubernetes-ingress haproxytech/kubernetes-ingress --create-namespace --namespace haproxy
```
## Expose Hubble-UI through Ingress
```
kubectl apply yaml/Cilium/hubble-ingress.yaml
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

Wait until the StatefulSet for RabbitMQ is online. From there you can get the default username and password.

```
username="$(kubectl -n signalwave get secret rabbitmq-default-user -o jsonpath='{.data.username}' | base64 --decode)"
echo "username: $username"
password="$(kubectl -n signalwave get secret rabbitmq-default-user -o jsonpath='{.data.password}' | base64 --decode)"
echo "password: $password"
```

### Access RabbitMQ UI
Using the username and password above, log into the RabbitMQ UI. From there create a new user with administrator privileges
that the SignalWave application will leverage.

## Installing ELK Stack (elasticsearch, kibana, and fluentd)
Create the namespace for the ELK stack:
```
kubectl create namespace kube-logging
```
Edit the `elasticsearch_pv.yaml` file to include the correct PV path for the local NFS server running in the environment.

```
kubectl create -f elasticsearch_pv.yaml
kubectl create -f elasticsearch_svc.yaml
kubectl create -f elasticsearch_statefulset.yaml
```

Edit the `kibana_pv.yaml` file to include the correct PV path for the local NFS server running in the environment.

```
kubectl create -f kibana_pv.yaml
kubectl create -f kibana_svc.yaml
kubectl create -f kibana_deployment.yaml
```

Deploy the fluentd application:
```
kubectl create -f fluentd_rbac.yaml
kubectl create -f fluentd_configmap.yaml
kubectl create -f fluentd_daemonset.yaml
```

## Install the custom SignalWave application
The first part of the SignalWave application is the Publisher microservice. The application is a small container housing a single script `publisher.py`.
The Publisher microservice gathers a number of networking metrics from the environment out to the 'virtualelephant.com' website as a means to monitor
different network latencies.

To start the microservice, execute the following command:
```
kubectl apply -f publisher.yaml
```

The SignalWave application has three additional microservices that make up the application. The data written to the RabbitMQ service will be pulled
off of the queue and input into an RRD compatible data format. From there the data is used to generate a number of graphs, one per metric, and finally the frontend
microservice runs NGINX to display the graphs in a HTML format running behind a HAProxy ingress object. 
```
kubectl apply -f rrd-reader.yaml
kubectl apply -f rrd-graph.yaml
kubectl apply -f frontend-nginx.yaml
kubectl apply -f frontend-ingress.yaml
```