# Kubernetes NLP Product Description Generator

A cloud-ready NLP system that generates product descriptions with GPT-2, exposes the model through a FastAPI backend, provides a Streamlit UI, and includes Docker, Kubernetes, Prometheus, and Grafana configuration for deployment and monitoring.

## Features

- FastAPI service for text generation, evaluation, health checks, readiness checks, and Prometheus metrics
- Streamlit UI for generating and evaluating product descriptions
- GPT-2 based product description generation using Hugging Face Transformers
- BLEU and ROUGE scoring for generated text evaluation
- Docker Compose setup for local API, UI, Prometheus, Grafana, and cAdvisor
- Kubernetes manifests for application deployment, scaling, ingress, and monitoring
- GitHub Actions workflow for CI/CD

## Project Structure

```text
.
├── app/
│   ├── api.py              # FastAPI backend
│   ├── app.py              # Streamlit frontend
│   ├── data.py             # Dataset helper
│   ├── metrics.py          # Prometheus metrics
│   └── model.py            # GPT-2 generation and evaluation logic
├── grafana/                # Grafana datasource and dashboard config
├── k8s/                    # Kubernetes manifests
├── prometheus/             # Prometheus config and alerts
├── tests/                  # Basic API tests
├── Dockerfile              # API image
├── Dockerfile.ui           # UI image
├── docker-compose.yml      # Local multi-service stack
├── requirements.txt        # Python dependencies
└── SETUP.md                # Full AWS EKS deployment guide
```

## Prerequisites

- Python 3.9+
- Docker Desktop
- Git
- For Kubernetes deployment: `kubectl`, AWS CLI, and `eksctl`

## Run Locally with Docker Compose

```powershell
docker compose up --build
```

After the services start:

| Service | URL |
| --- | --- |
| Streamlit UI | http://localhost:8054 |
| API docs | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| cAdvisor | http://localhost:8080 |

Default Grafana login:

```text
Username: admin
Password: admin123
```

## Run the API Manually

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt')"
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

In another terminal, run the UI:

```powershell
$env:API_URL = "http://localhost:8000"
streamlit run app/app.py --server.port 8054
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/ready` | Readiness check |
| `GET` | `/metrics` | Prometheus metrics |
| `POST` | `/generate` | Generate product description text |
| `POST` | `/evaluate` | Evaluate generated text against reference text |

Example generation request:

```powershell
curl -X POST http://localhost:8000/generate `
  -H "Content-Type: application/json" `
  -d '{"prompt":"Wireless noise-cancelling headphones with long battery life","max_new_tokens":80,"temperature":0.7,"top_k":50,"top_p":0.95}'
```

## Tests

```powershell
pytest
```

The current test suite checks basic FastAPI health and metrics endpoints without loading the full GPT-2 generation flow.

## Kubernetes Deployment

The Kubernetes manifests live in `k8s/`, with monitoring resources under `k8s/monitoring/` and Prometheus/Grafana configuration in their own folders.

For the full AWS EKS deployment flow, image build commands, port-forwarding, dashboard setup, and teardown steps, see [SETUP.md](SETUP.md).

## Notes

- The first API startup downloads and loads the GPT-2 model, so initial startup can take time.
- For EKS, use nodes with enough memory for model loading. The setup guide recommends `t3.large`.
- The generated model output depends on prompt quality and sampling settings such as temperature, `top_k`, and `top_p`.
