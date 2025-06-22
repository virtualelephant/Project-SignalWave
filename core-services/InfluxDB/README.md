# InfluxDB Installation Instructions

## Create the PVC

```bash
kubectl apply -f influxdb-pvc.yaml
```

## Create the Deployment

```bash
kubectl apply -f influxdb-deployment.yaml
```

## Create the Ingress object

```bash
kubectl apply -f influxdb-ingress.yaml
```