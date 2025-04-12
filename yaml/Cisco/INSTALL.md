```
kubectl create configmap snmp-exporter-config --from-file=snmp.yaml=./snmp.yaml
kubectl apply -f snmp-exporter.yaml
```