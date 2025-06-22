# Installing Prometheus and Grafana through Helm

The values file is setup to allow for scraping data from other services, as well as leveraging persistent storage from a storageclass object, 'standard-retain' which is created by the YAML found in yaml/SignalWave directory.

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
   --namespace monitoring \
   -f prometheus-values.yaml
```

# Create Ingress objects for Prometheus and Grafana

```bash
kubectl apply -f prometheus-grafana-ingress.yaml
```

# Get Grafana user password

```bash
kubectl --namespace monitoring get secrets prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo
```