# Installation Guide
- Current Version: v1.1
- Last Modified: 13.January.2025
- Maintainer: chris@virtualelephant.com

## Create Namespaces for Project SignalWave

```
kubectl create namespace signalwave
kubectl create namespace shared-services
kubectl create namespace monitoring
```

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
### Expose Hubble-UI through Ingress
```
kubectl apply yaml/Cilium/hubble-ingress.yaml
```

## Installing Prometheus and Grafana through Helm

The values file is setup to allow for scraping data from other services, as well as leveraging persistent storage from a storageclass object, 'standard-retain' which is created by the YAML found in yaml/SignalWave directory.

```
helm install prometheus prometheus-community/kube-prometheus-stack \
   --namespace monitoring \
   -f prometheus-values.yaml
```

### Create Ingress objects for Prometheus and Grafana

```
kubectl apply -f prometheus-grafana-ingress.yaml
```

## Installing RabbitMQ

I am moving away from deploying RabbitmQ with the Operator to doing it with Helm. The Helm leverages a values file and can be deployed with the following command:

```
helm install rabbitmq bitnami/rabbitmq \
  --namespace shared-services \
  --create-namespace \
  -f values.yaml
```

### Enabling Ingress for RabbitMQ

```
kubectl apply -f rabbitmq-ingress.yaml
```

### Access RabbitMQ UI
Using the username and password above, log into the RabbitMQ UI. From there create a new user with administrator privileges
that the SignalWave application will leverage.

## Deploying ELK through Helm

Add Bitnami Helm Repo (includes Fluentd)
```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

Add Elastic Helm Repo (inclused ElasticSearch and Kibana)
```
helm repo add elastic https://helm.elastic.co
helm repo update
```

Deploy the ELK Stack
```
helm install elasticsearch elastic/elasticsearch -n monitoring -f elasticsearch-values.yaml
helm install kibana elastic/kibana -n monitoring -f kibana-values.yaml
helm install fluentd bitnami/fluentd -n monitoring -f fluentd-values.yaml
kubectl apply -f kibana-ingress.yaml
```

Get the default username & password that Elastic generated
```
kubectl get secret elasticsearch-master-credentials -n monitoring -o go-template='{{.data.username | base64decode}}'
kubectl get secret elasticsearch-master-credentials -n monitoring -o go-template='{{.data.password | base64decode}}'
```

Go to the Web Console - http://kibana.YOUR.DOMAIN.NAME

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
kubectl apply -f rrd-storage.yaml
kubectl apply -f rrd-reader.yaml
kubectl apply -f rrd-graph.yaml
kubectl apply -f frontend-nginx.yaml
kubectl apply -f frontend-ingress.yaml
```