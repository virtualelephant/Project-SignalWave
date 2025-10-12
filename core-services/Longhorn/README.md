# Installing Longhorn Storage System

## Helm Installation Guide
```bash
helm repo add longhorn https://charts.longhorn.io
helm repo update
helm install longhorn longhorn/longhorn --namespace longhorn-system --create-namespace --version 1.9.2
```

## Create Basic Authentication
```bash
USER=<USERNAME_HERE>; PASSWORD=<PASSWORD_HERE>; echo "${USER}:$(openssl passwd -stdin -apr1 <<< ${PASSWORD})" >> auth
kubectl -n longhorn-system create secret generic basic-auth --from-file=auth
```

## Create Ingress for Longhorn
```bash
kubectl apply -f longhorn-ingress.yaml
```

## Create Retain Storage Policy for Longhorn
```bash
kubectl apply -f longhorn-retain-storage.yaml
```