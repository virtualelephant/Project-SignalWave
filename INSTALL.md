# Installation Guide
- Current Version: v1.3
- Maintainer: chris@virtualelephant.com

## Create Namespaces for Project SignalWave

```bash
kubectl create namespace signalwave
kubectl create namespace services
kubectl create namespace monitoring
kubectl create namespace codellama
```

## Installing NFS Client Provisioner
https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner

```bash
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
    --set nfs.server=x.x.x.x \
    --set nfs.path=/exported/path \
    --create-namespace \
    --namespace=nfs-storage
```

In the `yaml/SignalWave` directory, modify the `storageclass.yaml` file to point to the NFS server and apply it in the cluster.

```bash
kubectl apply -f storageclass.yaml
kubectl apply -f storageclass-retain.yaml
```

## Installing HAProxy Ingress Controller

```bash
helm repo add haproxytech https://haproxytech.github.io/helm-charts
helm install haproxy-kubernetes-ingress haproxytech/kubernetes-ingress --create-namespace --namespace haproxy
```
### Expose Hubble-UI through Ingress

```bash
kubectl apply yaml/Cilium/hubble-ingress.yaml
```

## Installing Prometheus and Grafana through Helm

The values file is setup to allow for scraping data from other services, as well as leveraging persistent storage from a storageclass object, 'standard-retain' which is created by the YAML found in yaml/SignalWave directory.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
   --namespace monitoring \
   -f prometheus-values.yaml
```

### Create Ingress objects for Prometheus and Grafana

```bash
kubectl apply -f prometheus-grafana-ingress.yaml
```

## Deploying ELK through Helm

Add Bitnami Helm Repo (includes Fluentd)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

Add Elastic Helm Repo (inclused ElasticSearch and Kibana)

```bash
helm repo add elastic https://helm.elastic.co
helm repo update
```

Deploy the ELK Stack

```bash
helm install elasticsearch elastic/elasticsearch -n services -f elasticsearch-values.yaml
helm install kibana elastic/kibana -n services -f kibana-values.yaml
helm install fluentd bitnami/fluentd -n services -f fluentd-values.yaml
kubectl apply -f kibana-ingress.yaml
```

Get the default username & password that Elastic generated:

```bash
kubectl get secret elasticsearch-master-credentials -n monitoring -o go-template='{{.data.username | base64decode}}'
kubectl get secret elasticsearch-master-credentials -n monitoring -o go-template='{{.data.password | base64decode}}'
```

Go to the Web Console - http://kibana.YOUR.DOMAIN.NAME

## Installing RabbitMQ

I am moving away from deploying RabbitmQ with the Operator to doing it with Helm. The Helm installation leverages a values file and can be deployed with the following command:

```bash
helm install rabbitmq bitnami/rabbitmq \
  --namespace shared-services \
  --create-namespace \
  -f values.yaml
```

### Enabling Ingress for RabbitMQ
The RabbitMQ application needs an external ingress object so that is can be accessed externally from the Kubernetes cluster. Run the following command to create the HAProxy ingress object:

```bash
kubectl apply -f rabbitmq-ingress.yaml
```

### Access RabbitMQ UI
Using the username and password above, log into the RabbitMQ UI. From there create a new user with administrator privileges
that the SignalWave application will leverage.

## Installing InfluxDB in the services namespace
InfluxDB is used throughout the Project SignalWave as a database layer for metrics that are being collected within the infrastructure layer (physical network, pfSense firewall, Synology array, etc.), as well as the software and application components within the Kubernetes cluster, Linux machines (VMs or bare metal), and other subcomponents of the entire platform.

To deploy InfluxDB within the `services` namespace, run the following commands:

```bash
kubectl apply -f influxdb-pvc.yaml
kubectl apply -f influxdb-deployment.yaml
kubectl apply -f influxdb-ingress.yaml
```

## Installing ArgoCD in the services namespace

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

helm upgrade --install argocd argo/argo-cd \
  -n services \
  -f argocd-values.yaml
```

## Install the SignalWave application
The first part of the SignalWave application is the Publisher microservice. The application is a small container housing a single script `publisher.py`.

The Publisher microservice gathers a number of networking metrics from the environment out to the 'virtualelephant.com' website as a means to monitor different network latencies.

To start the microservice, execute the following command:
```bash
kubectl apply -f publisher.yaml
```

The second part of the SignalWave application is the Influx Reader microservice. The application is a small container housing a single script `influx-writer.py`. The Python script reads the metrics off of the RabbitMQ queue and then writes the metrics data into the InfluxDB `monitoring` bucket running in the `services` namespace.

```bash
kubectl apply -f influxdb-secret.yaml
kubectl apply -f influx-reader.yaml
```

From there, a custom Grafana dashboard leverages the data metrics to create a dashboard showing external connectivity to the given set of external websites for the user to monitor. Alerts can be generated through Grafana based on connectivity latency or if the site goes offline for longer than X polling intervals.

## Install local CodeLlama AI Model

***This is currently a WIP and modifications may be required***

Having a local model to run internally and then train it based off the type of projects and coding I am working on is a good exercise is learning more about AI models and what it takes to writes agents, interfaces, etc. Using Grok, I've built a backend that leverages the CodeLlama-7B model (https://huggingface.co/codellama/CodeLlama-7b-hf). The frontend then provides a way of interacting with the AI model to write code.

To build the containers required:

```bash
cd containers/codellama-backend
docker build -t --no-cache codellama-backend:latest .
docker push YOUR.REPO/LIBRARY/codellama-backend:lastest

cd containers/codellama-frontend
docker build -t --no-cache codellama-frontend:latest .
docker push YOUR.REPO/LIBRARY/codellama-frontend:latest
```

To run the AI model inside Kubernetes:

```bash
kubectl create namespace codellama
kubectl apply yaml/CodeLlama-7B/codellama-deployment.yaml
kubectl apply yaml/CodeLlama-7B/codellama-frontend-deployment.yaml
kubectl apply yaml/CodeLlama-7B/codellama-frontend-ingress.yaml
```