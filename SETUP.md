# Cloud-Based NLP Product Description System
## Complete Setup Guide — All Commands

---

## Prerequisites

Install these before starting:
- Docker Desktop
- kubectl
- AWS CLI
- eksctl

---

## Step 1 — Configure AWS CLI

```powershell
aws configure
```
Enter when prompted:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: ap-south-1
- Default output format: json

Verify:
```powershell
aws sts get-caller-identity
```

---

## Step 2 — Set Environment Variables

Run these one at a time in every new PowerShell session:

```powershell
$AWS_ACCOUNT = aws sts get-caller-identity --query Account --output text
$AWS_REGION = "ap-south-1"
$ECR = "$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com"
echo $ECR
```

---

## Step 3 — Create EKS Cluster

```powershell
eksctl create cluster `
  --name nlp-cluster `
  --region ap-south-1 `
  --nodegroup-name workers `
  --node-type t3.large `
  --nodes 2 `
  --nodes-min 2 `
  --nodes-max 5 `
  --managed
```
*(Note: t3.large is recommended over t3.medium to load GPT-2 models.)*

Verify cluster is ready:
```powershell
kubectl get nodes
```

---

## Step 4 — Create ECR Repositories

```powershell
aws ecr create-repository --repository-name nlp-prediction-api --region ap-south-1
aws ecr create-repository --repository-name nlp-prediction-ui --region ap-south-1
```

---

## Step 5 — Login Docker to ECR

```powershell
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ECR
```

---

## Step 6 — Build and Push Docker Images

```powershell
docker build --no-cache -t $ECR/nlp-prediction-api:v1 .
docker push $ECR/nlp-prediction-api:v1

docker build -f Dockerfile.ui -t $ECR/nlp-prediction-ui:latest .
docker push $ECR/nlp-prediction-ui:latest
```

---

## Step 7 — Create Kubernetes Namespace

```powershell
kubectl apply -f k8s/base/namespace.yaml
```

---

## Step 8 — Deploy the Application

```powershell
kubectl apply -f k8s/base/deployment.yaml
kubectl apply -f k8s/base/hpa-ingress.yaml
```

---

## Step 9 — Deploy Monitoring Stack (Prometheus + Grafana)

```powershell
kubectl apply -f k8s/monitoring/monitoring-stack.yaml
kubectl apply -f prometheus/prometheus-config.yaml
```

---

## Step 10 — Verify All Pods Are Running

```powershell
kubectl get pods -n nlp-prediction
```

Expected output:
```
grafana-xxx                  1/1   Running
prometheus-xxx               1/1   Running
nlp-prediction-api-xxx       1/1   Running
nlp-prediction-api-xxx       1/1   Running
nlp-prediction-ui-xxx        1/1   Running
```

---

## Step 11 — Access Services (Port Forwarding)

Open 4 separate PowerShell terminals and run one command in each:

**Terminal 1 — API:**
```powershell
kubectl port-forward svc/nlp-prediction-api-service 8000:8000 -n nlp-prediction
```

**Terminal 2 — Streamlit UI:**
```powershell
kubectl port-forward svc/nlp-prediction-ui-service 8054:8054 -n nlp-prediction
```

**Terminal 3 — Prometheus:**
```powershell
kubectl port-forward svc/prometheus-service 9090:9090 -n nlp-prediction
```

**Terminal 4 — Grafana:**
```powershell
kubectl port-forward svc/grafana-service 3001:3000 -n nlp-prediction
```

---

## Step 12 — URLs

| Service        | URL                        | Credentials         |
|----------------|----------------------------|---------------------|
| Streamlit UI   | http://localhost:8054       | —                   |
| API Docs       | http://localhost:8000/docs  | —                   |
| Prometheus     | http://localhost:9090       | —                   |
| Grafana        | http://localhost:3001       | admin / admin123    |

---

## Step 13 — Set Up Grafana Dashboard

1. Open http://localhost:3001 → login: admin / admin123
2. Go to **Connections → Data Sources → Add data source**
3. Select **Prometheus**
4. Set URL to: `http://prometheus-service:9090`
5. Click **Save & Test**
6. Go to **Dashboards → Import**
7. Click **Upload dashboard JSON file**
8. Upload `grafana/dashboards/nlp-prediction.json`
9. Select your Prometheus data source → click **Import**

---

## Step 14 — Test the API

```powershell
curl http://localhost:8000/health
```

---

## Tear Down (Delete Everything)

```powershell
# Delete all Kubernetes resources
kubectl delete namespace nlp-prediction

# Delete EKS cluster (stops AWS charges)
eksctl delete cluster --name nlp-cluster --region ap-south-1

# Delete ECR repositories
aws ecr delete-repository --repository-name nlp-prediction-api --region ap-south-1 --force
aws ecr delete-repository --repository-name nlp-prediction-ui --region ap-south-1 --force
```
