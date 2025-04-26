# Installing RabbitMQ

I am moving away from deploying RabbitmQ with the Operator to doing it with Helm. The Helm leverages a values file and can be deployed with the following command:

```
helm install rabbitmq bitnami/rabbitmq \
  --namespace services \
  -f rabbitmq-values.yaml
```

# Enabling Ingress for RabbitMQ

```
kubectl apply -f rabbitmq-ingress.yaml
```