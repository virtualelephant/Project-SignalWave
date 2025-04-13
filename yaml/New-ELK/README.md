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

Deploy ElasticSearch
```
helm install elasticsearch elastic/elasticsearch -n monitoring -f elasticsearch-values.yaml
helm install kibana elastic/kibana -n monitoring -f kibana-values.yaml
```