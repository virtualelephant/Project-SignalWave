# Deploying ELK through Helm

Add Bitnami Helm Repo (includes Fluentd)
```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

Add Elastic Helm Repo (inclused ElasticSearch and Kibana)
```
helm repo add elastic https://helm.elastic.co
helm repo update
```

Deploy the ELK Stack
```
helm install elasticsearch elastic/elasticsearch -n monitoring -f elasticsearch-values.yaml
helm install kibana elastic/kibana -n monitoring -f kibana-values.yaml
helm install fluentd bitnami/fluentd -n monitoring -f fluentd-values.yaml
kubectl apply -f kibana-ingress.yaml
```

Get the default username & password that Elastic generated
```
kubectl get secret elasticsearch-master-credentials -n monitoring -o go-template='{{.data.username | base64decode}}'
kubectl get secret elasticsearch-master-credentials -n monitoring -o go-template='{{.data.password | base64decode}}'
```

Go to the Web Console - http://kibana.YOUR.DOMAIN.NAME