
## Create the secret for the InfluxDB Service
```
kubectl create secret generic influxdb-auth \
  --from-literal=token=eQXgVC95W4n0OfnpM5w6LzFIgGNOpGSkIWLW8IwESyOrdzQUm0hU10aKNKUovbYdZRrpA5ZgY4z6CLa08SspkA== \
  -n apps
```

## Create the secret for Visual Crossing Weather data
```
kubectl create secret generic weather-api \
  --from-literal=api-key=PASTE_YOUR_KEY \
  -n apps