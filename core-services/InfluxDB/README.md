# InfluxDB Installation Instructions

## Create the PVC

```bash
kubectl apply -f influxdb-pvc.yaml
```

## Create the Deployment

```bash
kubectl apply -f influxdb-deployment.yaml
```

## Use either the Gateway API or Ingress YAML Files
## Create the Gateway API Objects
These work with the Cilium IP Pools and Gateway API implementation. This is the preferred way of doing things.

```bash
kubectl apply -f 01-certificate-influxdb.yaml
kubectl apply -f 02-gateway-influxdb.yaml
kubectl apply -f 03-httproute-influxdb.yaml
kubectl apply -f 04-httproute-redirect.yaml
```

## Create the Ingress object

```bash
kubectl apply -f influxdb-ingress-haproxy.yaml
```

or 

```bash
kubectl apply -f influxdb-ingress-nginx.yaml
```

# Tokens
## Prod Token for virtualelephant organization, prod bucket
```bash
3zwSlNd5_QD-yxSGss4kmhFB4VE-kWOh0W5J0Tx980P1rtxq1VQd0wCP4ZA5aHOofQZ2zR-dEn78Tp6q0Z0O7g==
```