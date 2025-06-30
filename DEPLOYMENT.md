# CMU Health Services RAG Chatbot - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the CMU Health Services RAG Chatbot to Google Cloud Platform (GCP) using Docker containers and Kubernetes.

## Architecture

The deployment consists of:
- **Frontend**: Next.js application served via Nginx
- **Backend**: Spring Boot API with LangChain4j
- **Database**: PostgreSQL with pgvector extension
- **Cache**: Redis for performance optimization
- **Orchestration**: Google Kubernetes Engine (GKE)

## Prerequisites

1. **Local Development Tools**
   - Docker Desktop installed
   - `gcloud` CLI installed
   - `kubectl` installed
   - Node.js 20+ and Java 17+

2. **GCP Account**
   - Active GCP project with billing enabled
   - Required permissions: Project Editor or Owner

3. **API Keys**
   - OpenAI API key for GPT-3.5-turbo
   - GCP service account (created automatically)

## Quick Start

### 1. Local Testing with Docker Compose

```bash
# Clone the repository
git clone https://github.com/your-org/CMU-UHS-RAG-CHATBOT.git
cd CMU-UHS-RAG-CHATBOT

# Copy environment variables
cp .env.example .env
# Edit .env with your values

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8080
```

### 2. Deploy to GCP

```bash
# Run the automated deployment script
chmod +x deploy/gcp-deploy.sh
./deploy/gcp-deploy.sh
```

The script will:
1. Authenticate with GCP
2. Enable required APIs
3. Build and push Docker images
4. Create GKE cluster
5. Deploy all services
6. Configure load balancer

## Manual Deployment Steps

### Step 1: Set Up Environment

```bash
# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export GCP_ZONE="us-central1-a"
export GKE_CLUSTER_NAME="cmu-rag-cluster"

# Authenticate
gcloud auth login
gcloud config set project ${GCP_PROJECT_ID}
```

### Step 2: Build Docker Images

```bash
# Backend
cd backend
docker build -t gcr.io/${GCP_PROJECT_ID}/cmu-rag-backend:latest .

# Frontend
cd ../frontend
docker build -t gcr.io/${GCP_PROJECT_ID}/cmu-rag-frontend:latest .
```

### Step 3: Push to Container Registry

```bash
# Configure Docker
gcloud auth configure-docker

# Push images
docker push gcr.io/${GCP_PROJECT_ID}/cmu-rag-backend:latest
docker push gcr.io/${GCP_PROJECT_ID}/cmu-rag-frontend:latest
```

### Step 4: Create GKE Cluster

```bash
gcloud container clusters create ${GKE_CLUSTER_NAME} \
  --num-nodes=3 \
  --machine-type=e2-standard-2 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=10
```

### Step 5: Deploy to Kubernetes

```bash
# Get cluster credentials
gcloud container clusters get-credentials ${GKE_CLUSTER_NAME}

# Create namespace
kubectl create namespace cmu-rag

# Create secrets
kubectl create secret generic cmu-rag-secrets \
  --from-literal=openai-api-key=${OPENAI_API_KEY} \
  --from-literal=postgres-password=${POSTGRES_PASSWORD} \
  --namespace=cmu-rag

# Apply manifests
kubectl apply -f deploy/k8s/ --namespace=cmu-rag
```

## Configuration

### Environment Variables

Key environment variables to configure:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `POSTGRES_PASSWORD` | Database password | `secure-password` |
| `REDIS_PASSWORD` | Redis password | `redis-password` |
| `JWT_SECRET` | JWT signing secret | `your-secret-key` |

### Application Configuration

1. **Backend** (`application-docker.yml`):
   - Database connections
   - Redis configuration
   - OpenAI settings
   - CORS policies

2. **Frontend** (`next.config.js`):
   - API endpoint URLs
   - Security headers
   - Image optimization

## Monitoring

### Health Checks

- Frontend: `http://<IP>/api/health`
- Backend: `http://<IP>/actuator/health`

### Logs

```bash
# View backend logs
kubectl logs -f deployment/backend -n cmu-rag

# View frontend logs
kubectl logs -f deployment/frontend -n cmu-rag
```

### Metrics

Access Prometheus metrics at:
- `http://<IP>/actuator/prometheus`

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment/backend --replicas=5 -n cmu-rag

# Scale frontend
kubectl scale deployment/frontend --replicas=3 -n cmu-rag
```

### Auto-scaling

Horizontal Pod Autoscalers are configured to scale based on:
- CPU utilization > 70%
- Memory utilization > 80%

## Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name> -n cmu-rag
   kubectl logs <pod-name> -n cmu-rag
   ```

2. **Database connection errors**
   - Check PostgreSQL pod status
   - Verify credentials in secrets
   - Check network policies

3. **External IP not assigned**
   - Wait 2-5 minutes for provisioning
   - Check service status: `kubectl get svc -n cmu-rag`

### Debug Commands

```bash
# Get all resources
kubectl get all -n cmu-rag

# Check events
kubectl get events -n cmu-rag --sort-by='.lastTimestamp'

# Enter pod shell
kubectl exec -it <pod-name> -n cmu-rag -- /bin/sh
```

## Security Best Practices

1. **Secrets Management**
   - Use Google Secret Manager for production
   - Rotate API keys regularly
   - Never commit secrets to git

2. **Network Security**
   - Configure firewall rules
   - Use private GKE clusters
   - Enable network policies

3. **Updates**
   - Enable auto-upgrades for GKE
   - Keep dependencies updated
   - Monitor security advisories

## Cost Optimization

Estimated monthly costs:
- GKE cluster (3 nodes): ~$150
- Cloud SQL: ~$50
- Redis: ~$30
- Load Balancer: ~$18
- **Total**: ~$248/month

Tips to reduce costs:
1. Use preemptible nodes for non-critical workloads
2. Enable cluster autoscaler
3. Use committed use discounts
4. Monitor and optimize resource requests

## Backup and Recovery

### Database Backup

```bash
# Manual backup
gcloud sql backups create \
  --instance=cmu-rag-postgres \
  --description="Manual backup $(date +%Y%m%d)"

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --restore-instance=cmu-rag-postgres
```

### Application State

- Embeddings: Stored in PostgreSQL
- Cache: Redis (can be rebuilt)
- Uploads: Consider Cloud Storage for persistence

## CI/CD Pipeline

See `.github/workflows/deploy.yml` for automated deployment on push to main branch.

## Support

For issues or questions:
1. Check logs and events
2. Review this documentation
3. Open an issue on GitHub
4. Contact the development team

---

Last updated: December 2024