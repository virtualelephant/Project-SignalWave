```
helm install prometheus prometheus-community/kube-prometheus-stack \
   --namespace monitoring \
   -f prometheus-values.yaml