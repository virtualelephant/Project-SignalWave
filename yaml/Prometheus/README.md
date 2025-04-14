# Installing Prometheus and Grafana through Helm

The values file is setup to allow for scraping data from other services, as well as leveraging persistent storage from a storageclass object, 'standard-retain' which is created by the YAML found in yaml/SignalWave directory.

```
helm install prometheus prometheus-community/kube-prometheus-stack \
   --namespace monitoring \
   -f prometheus-values.yaml
```