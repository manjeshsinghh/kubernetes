"""
FastAPI Backend for NLP Product Description Generator
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import time
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .model import ProductDescriptionGenerator
from .metrics import REQUEST_COUNT, REQUEST_LATENCY, GENERATION_TIME, MODEL_CALLS

app = FastAPI(title="NLP Product Description API")

# Initialize model globally
generator = None

@app.on_event("startup")
def startup_event():
    global generator
    # We load model on startup. In production this can take a few seconds
    generator = ProductDescriptionGenerator()

@app.middleware("http")
async def add_prometheus_metrics(request: Request, call_next):
    method = request.method
    path = request.url.path
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    status_code = response.status_code
    
    # Only track API endpoints to avoid noise
    if path in ["/generate", "/evaluate", "/health"]:
        REQUEST_COUNT.labels(method=method, endpoint=path, http_status=status_code).inc()
        REQUEST_LATENCY.labels(endpoint=path).observe(process_time)
    
    return response

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": generator is not None}

@app.get("/ready")
def readiness_check():
    return {"status": "ready", "model_loaded": generator is not None}

class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 150
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.95

@app.post("/generate")
def generate_description(request: GenerateRequest):
    if not generator:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    start_time = time.time()
    try:
        generated_text = generator.generate_text(
            request.prompt,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p
        )
        MODEL_CALLS.labels(status="success").inc()
    except Exception as e:
        MODEL_CALLS.labels(status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        process_time = time.time() - start_time
        GENERATION_TIME.observe(process_time)
        
    return {"generated_text": generated_text}

class EvaluateRequest(BaseModel):
    generated_text: str
    reference_text: str

@app.post("/evaluate")
def evaluate(request: EvaluateRequest):
    if not generator:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    scores = generator.reward_function(request.generated_text, request.reference_text)
    return scores
