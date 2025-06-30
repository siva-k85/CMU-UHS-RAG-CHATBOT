#!/bin/bash

# CMU Health Services RAG Chatbot - GCP Deployment Script
# This script automates the deployment process to Google Cloud Platform

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    print_error ".env file not found. Please create one from .env.example"
    exit 1
fi

# Validate required environment variables
required_vars=("GCP_PROJECT_ID" "GCP_REGION" "GCP_ZONE" "GKE_CLUSTER_NAME" "OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set"
        exit 1
    fi
done

# Set default values
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"gcr.io"}
DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG:-"latest"}

print_status "Starting GCP deployment for CMU Health Services RAG Chatbot"

# Step 1: Authenticate with GCP
print_status "Authenticating with Google Cloud..."
gcloud auth login
gcloud config set project ${GCP_PROJECT_ID}
gcloud config set compute/region ${GCP_REGION}
gcloud config set compute/zone ${GCP_ZONE}

# Step 2: Enable required APIs
print_status "Enabling required GCP APIs..."
gcloud services enable \
    container.googleapis.com \
    cloudbuild.googleapis.com \
    cloudresourcemanager.googleapis.com \
    compute.googleapis.com \
    sqladmin.googleapis.com \
    redis.googleapis.com \
    artifactregistry.googleapis.com

# Step 3: Create Artifact Registry repository (if not exists)
print_status "Creating Artifact Registry repository..."
gcloud artifacts repositories create cmu-rag-repo \
    --repository-format=docker \
    --location=${GCP_REGION} \
    --description="CMU RAG Chatbot Docker images" || true

# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev

# Step 4: Build and push Docker images
print_status "Building Docker images..."

# Build backend
print_status "Building backend Docker image..."
cd backend
docker build -t ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cmu-rag-repo/backend:${DOCKER_IMAGE_TAG} .

# Build frontend
print_status "Building frontend Docker image..."
cd ../frontend
docker build -t ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cmu-rag-repo/frontend:${DOCKER_IMAGE_TAG} .

cd ..

# Push images to registry
print_status "Pushing Docker images to Artifact Registry..."
docker push ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cmu-rag-repo/backend:${DOCKER_IMAGE_TAG}
docker push ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cmu-rag-repo/frontend:${DOCKER_IMAGE_TAG}

# Step 5: Create GKE cluster (if not exists)
print_status "Creating GKE cluster..."
gcloud container clusters create ${GKE_CLUSTER_NAME} \
    --num-nodes=3 \
    --machine-type=e2-standard-2 \
    --disk-size=50 \
    --enable-autoscaling \
    --min-nodes=2 \
    --max-nodes=10 \
    --enable-autorepair \
    --enable-autoupgrade \
    --release-channel=regular \
    --network=default \
    --subnetwork=default \
    --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
    --workload-pool=${GCP_PROJECT_ID}.svc.id.goog || true

# Get cluster credentials
print_status "Getting cluster credentials..."
gcloud container clusters get-credentials ${GKE_CLUSTER_NAME} --region=${GCP_REGION}

# Step 6: Create Cloud SQL instance for PostgreSQL
print_status "Creating Cloud SQL PostgreSQL instance..."
gcloud sql instances create cmu-rag-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-g1-small \
    --region=${GCP_REGION} \
    --network=default \
    --database-flags=cloudsql.enable_pgvector=on \
    --root-password=${POSTGRES_PASSWORD} || true

# Create database and user
print_status "Creating database and user..."
gcloud sql databases create cmu_health_rag --instance=cmu-rag-postgres || true
gcloud sql users create raguser --instance=cmu-rag-postgres --password=${POSTGRES_PASSWORD} || true

# Step 7: Create Redis instance
print_status "Creating Redis instance..."
gcloud redis instances create cmu-rag-redis \
    --size=1 \
    --region=${GCP_REGION} \
    --redis-version=redis_7_0 || true

# Step 8: Create Kubernetes namespace
print_status "Creating Kubernetes namespace..."
kubectl create namespace cmu-rag || true

# Step 9: Create Kubernetes secrets
print_status "Creating Kubernetes secrets..."
kubectl create secret generic cmu-rag-secrets \
    --from-literal=openai-api-key=${OPENAI_API_KEY} \
    --from-literal=postgres-password=${POSTGRES_PASSWORD} \
    --from-literal=redis-password=${REDIS_PASSWORD} \
    --from-literal=jwt-secret=${JWT_SECRET} \
    --namespace=cmu-rag \
    --dry-run=client -o yaml | kubectl apply -f -

# Step 10: Apply Kubernetes manifests
print_status "Deploying application to Kubernetes..."
kubectl apply -f deploy/k8s/ --namespace=cmu-rag

# Step 11: Wait for deployments to be ready
print_status "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=600s deployment/backend --namespace=cmu-rag
kubectl wait --for=condition=available --timeout=600s deployment/frontend --namespace=cmu-rag

# Step 12: Get external IP
print_status "Getting external IP address..."
EXTERNAL_IP=$(kubectl get service frontend-service -n cmu-rag -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

while [ -z "$EXTERNAL_IP" ]; do
    print_status "Waiting for external IP..."
    sleep 10
    EXTERNAL_IP=$(kubectl get service frontend-service -n cmu-rag -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
done

print_success "Deployment completed successfully!"
print_success "Application is available at: http://${EXTERNAL_IP}"
print_success "Backend API is available at: http://${EXTERNAL_IP}/api"

# Optional: Set up DNS
print_status "To set up DNS, create an A record pointing to: ${EXTERNAL_IP}"

# Display deployment info
print_status "Deployment Summary:"
echo "  Project ID: ${GCP_PROJECT_ID}"
echo "  Region: ${GCP_REGION}"
echo "  Cluster: ${GKE_CLUSTER_NAME}"
echo "  External IP: ${EXTERNAL_IP}"
echo ""
echo "Useful commands:"
echo "  View pods: kubectl get pods -n cmu-rag"
echo "  View logs: kubectl logs -f deployment/backend -n cmu-rag"
echo "  Scale deployment: kubectl scale deployment/backend --replicas=3 -n cmu-rag"