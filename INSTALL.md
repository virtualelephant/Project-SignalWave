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
The script generates 500 random log messages per execution with a 1 second delay. The container is setup to run the script every minute through CRON.

To start the microservice, execute the following command:
```
kubectl apply -f publisher.yaml
```

The second part of the SignalWave application is the Reader microservice. This part of the application reads from the RabbitMQ queue the Publisher microservice wrote the log messages to.
The microservice requires a PV to write the messages it reads off of the RabbitMQ queue that is then shared with the NGINX microservice.

To start the microservice for the Reader and NGINX, execute the following commands:
```
kubectl apply -f frontend-storage.yaml
kubectl apply -f html-configmap.yaml
kubectl apply -f frontend-reader.yaml
kubectl apply -f frontend.yaml
kubectl apply -f frontend-ingress.yaml
```