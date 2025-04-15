# Weather Application for Kubernetes
This app was written to grab historical and current weather data for a set of cities. The data is stored inside InfluxDB running inside the `monitoring` namespace and is then displayed inside a Grafana Dashboard for consumption.

## Create the secret for the InfluxDB Service
```
kubectl create secret generic influxdb-auth \
  --from-literal=token=kYSjhiuYiY0RP9W7mO6R2evwl2dbhz3H8wooyNNKsCXlieNr5KZNNbSrO6iZpNjGdSrC3nbEhwJhYpHrLmZunw== \
  -n signalwave
```

## Deploy the Current Weather Cronjob
```
kubectl apply -f current-weather-cronjob.yaml
kubectl get cronjobs -n apps
kubectl get jobs -n apps
kubectl logs job/<job-name> -n apps
```

## Deploy the Historical Weather Conjob
```
kubectl apply -f historical-weather-cronjob.yaml
kubectl get cronjobs -n apps
kubectl get jobs -n apps
kubectl logs job/<job-name> -n apps
```