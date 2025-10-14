# Deploying ELK through Helm

Add (new) Fluentd Helm Repo (includes Fluentd)
```
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update
```

Add Elastic Helm Repo (inclused ElasticSearch and Kibana)
```
helm repo add elastic https://helm.elastic.co
helm repo update
```

Deploy the ELK Stack
```
helm install elasticsearch elastic/elasticsearch -n services -f elasticsearch-values.yaml
helm install kibana elastic/kibana -n services -f kibana-values.yaml
helm install fluentd bitnami/fluentd -n services -f fluentd-values.yaml
kubectl apply -f kibana-ingress.yaml
```

Get the default username & password that Elastic generated
```
kubectl get secret elasticsearch-master-credentials -n services -o go-template='{{.data.username | base64decode}}'
kubectl get secret elasticsearch-master-credentials -n services -o go-template='{{.data.password | base64decode}}'
```

Go to the Web Console - http://kibana.YOUR.DOMAIN.NAME