# Installing Longhorn Storage System

## Helm Installation Guide
```
helm repo add longhorn https://charts.longhorn.io
helm repo update
helm install longhorn longhorn/longhorn --namespace longhorn-system --create-namespace --version 1.8.1
```

## Create Basic Authentication
```
USER=<USERNAME_HERE>; PASSWORD=<PASSWORD_HERE>; echo "${USER}:$(openssl passwd -stdin -apr1 <<< ${PASSWORD})" >> auth
kubectl -n longhorn-system create secret generic basic-auth --from-file=auth
```

## Create Ingress for Longhorn
```
kubectl apply -f longhorn-ingress.yaml
```