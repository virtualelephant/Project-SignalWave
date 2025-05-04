# CodeLlama-7B CPU-Based Local Model
The solution will:

1. Deploy CodeLlama-7B locally in Kubernetes with persistent storage using the `standard-retain` storage class.
2. Provide a React frontend that stores and displays chat history in PostgreSQL.
3. Periodically fine-tune CodeLlama-7B using your prompts, source code, and API interactions, stored in PostgreSQL.
4. Keep everything CPU-based, optimized for older Dell R630 servers without GPUs.

## Components

* Backend (FastAPI): Serves CodeLlama-7B, handles inference, and stores prompts/responses in PostgreSQL.
* Frontend (React): Allows users to interact with CodeLlama and view chat history.
* PostgreSQL: Stores chat history and fine-tuning data persistently.
* Fine-Tuning Jobs: Periodically fine-tunes CodeLlama using data from PostgreSQL, optimized for CPUs.

## Repo Structure
```text
codellama-project/
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
├── fine-tuning/
│   ├── Dockerfile
│   ├── fine_tune.py
│   ├── extract_dataset.py
│   ├── requirements.txt
├── kubernetes/
│   ├── codellama-deployment.yaml
│   ├── codellama-service.yaml
│   ├── codellama-frontend-deployment.yaml
│   ├── codellama-frontend-service.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── postgres-pvc.yaml
│   ├── fine-tune-job.yaml
│   ├── fine-tune-cronjob.yaml
├── README.md
├── INSTALL.md
```

## Understanding LLMs in an Engineering Organization

This setup provides a practical learning experience for adopting and improving LLMs:

* Pre-Trained Model: CodeLlama-7B offers a strong starting point for code-related tasks.
* Fine-Tuning: LoRA enables efficient customization on CPUs, mirroring how organizations adapt models to proprietary data.
* Production-Readiness: PostgreSQL and Kubernetes reflect enterprise-grade infrastructure.
* Iterative Improvement: Periodic fine-tuning with curated data (source code, APIs) demonstrates how to align LLMs with organizational needs.
* Challenges: CPU-based fine-tuning is slow, highlighting the trade-offs of hardware constraints (a common consideration for organizations without GPUs).

This solution deploys CodeLlama-7B in Kubernetes with persistent storage, a React frontend with PostgreSQL-backend chat history, and weekly fine-tuning using LoRA, all optimized for a CPU-based environment.

---
## Worker Node Requirements
Below are the resource requirements for each component and their impact on the Kubernetes worker nodes.

### CodeLlama Backend
* Deployment: `codellama-deployment`
* Resources:
    * Requests: 4 CPU, 8Gi RAM
    * Limits: 8 CPU, 16Gi RAM
* Storage: 50Gi PVC (`standard-retain`) for model weights (~14Gi for CodeLlama-7B quantized) and fine-tuned weights.
* Notes: Requires significant RAM for model inference. CPU usage spikes during inference but averages lower during idle periods.

### CodeLlama Frontend
* Deployment: `codellama-frontend-deployment`
* Resources:
    * Requests: 0.25 CPU, 256Mi RAM
    * Limits: 0.5 CPU, 512Mi RAM
* Storage: None (stateless)
* Notes: Lightweight, minimal impact on nodes

### PostgreSQL
* Deployment: `postgres-deployment`
* Resources:
    * Requests: 0.5 CPU, 512Mi RAM
    * Limits: 1 CPU, 1Gi RAM
* Storage: 10Gi PVC (`standard-retain`) for database data.
* Notes: Low CPU/RAM usage for a home lab. Storage grows with chat history (expect <1Gi for thousands of entries)

### Fine-Tuning Job
* Job/CrontJob: `codellama-fine-tune`, `codellama-fine-tune-cron`
* Resources:
    * Requests: 8 CPU, 16Gi RAM
    * Limits: 16 CPU, 32Gi RAM
* Storage: Uses the same 50Gi `codellama-pvc` for dataset and fine-tuned weights.
* Notes: Resource-intensive, runs weekly. LoRA reduces memory needs, but fine-tuning CPUs is slow (hours to days for 100-1000 examples).

## Node Recommendations:
* Minimum per Node: 16 cores, 32Gi RAM to handle steady-state and fine-tuning without contention.
* Ideal per Node: 24-32 Cores, 64Gi RAM to ensure smooth operation, especially during fine-tuning.

## Scaling Considerations:
* Use Kubernetes node selectors or taints to dedicate a high-resource node for fine-tuning.
* Monitor resource usage with Prometheus/Grafana to adjust requests/limits.