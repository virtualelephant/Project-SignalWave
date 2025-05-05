# Deployment Instructions

## Build and Push Docker Images:

* Backend
```bash
cd backend
docker build --no-cache -t harbor.home.virtualelephant.com/ve-lab/codellama-ai:latest .
docker push harbor.home.virtualelephant.com/ve-lab/codellama-ai:latest
```

* Frontend
```bash
cd frontend
docker build --no-cache -t harbor.home.virtualelephant.com/ve-lab/codellama-frontend:latest .
docker push harbor.home.virtualelephant.com/ve-lab/codellama-frontend:latest
```

* Fine-Tuning
```bash
cd fine-tuning
docker build --no-cache -t harbor.home.virtualelephant.com/ve-lab/codellama-fine-tuning:latest .
docker push harbor.home.virtualelephant.com/ve-lab/codellama-fine-tuning:latest
```

## Deploy to Kubernetes

```bash
cd kubernetes
kubectl create namespace codellama
kubectl apply -f postgres-pvc.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml

kubectl apply -f codellama-pvc.yaml
kubectl apply -f codellama-deployment.yaml
kubectl apply -f codellama-service.yaml

kubectl apply -f codellama-frontend-deployment.yaml
kubectl apply -f codellama-frontend-service.yaml
kubectl apply -f codellama-frontend-ingress.yaml

kubectl apply -f fine-tune-job.yaml
kubectl apply -f fine-tune-cronjob.yaml
```

