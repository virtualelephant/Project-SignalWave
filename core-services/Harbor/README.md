# Harbor Installation in Kubernetes using Helm

## SSL wildcard certificate
```bash
kubectl create secret tls harbor-tls \
  --cert=home.virtualelephant.com.bundle.crt \
  --key=home.virtualelephant.com.key \
  -n services
```
