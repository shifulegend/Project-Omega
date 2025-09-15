#!/usr/bin/env python3
"""
Project Omega - Simple API Server
High-Reasoning Uncensored LLM API

Author: MiniMax Agent
Created: September 15, 2025
"""

import os
import json
import time
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    import requests
except ImportError:
    print("Installing required packages...")
    os.system("pip install fastapi uvicorn requests pydantic")
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('omega.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("omega")

# Configuration
CONFIG = {
    "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", "dolphin-mistral:7b"),
    "MAX_TOKENS": int(os.getenv("MAX_TOKENS", "4096")),
    "TEMPERATURE": float(os.getenv("TEMPERATURE", "0.7")),
    "TOP_P": float(os.getenv("TOP_P", "0.9")),
    "HOST": os.getenv("API_HOST", "0.0.0.0"),
    "PORT": int(os.getenv("API_PORT", "8000")),
    "OLLAMA_URL": "http://localhost:11434",
}

# FastAPI app
app = FastAPI(
    title="Project Omega API",
    description="High-Reasoning Uncensored LLM API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stream: Optional[bool] = False
    system_prompt: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    timestamp: str
    tokens_used: Optional[int] = None
    generation_time: Optional[float] = None
    
class ModelInfo(BaseModel):
    name: str
    size: str
    family: str
    parameter_size: str
    quantization: str
    
class SystemStatus(BaseModel):
    status: str
    ollama_connected: bool
    models_available: int
    default_model: str
    gpu_info: Optional[Dict[str, Any]] = None
    uptime: str

# Global variables
start_time = datetime.now()

# Helper functions
def get_gpu_info():
    """Get GPU information"""
    try:
        import subprocess
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu',
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            gpus = []
            for line in lines:
                parts = line.split(', ')
                if len(parts) >= 5:
                    gpus.append({
                        "name": parts[0],
                        "memory_total": f"{parts[1]} MB",
                        "memory_used": f"{parts[2]} MB",
                        "memory_free": f"{parts[3]} MB",
                        "temperature": f"{parts[4]}°C"
                    })
            return gpus
    except Exception:
        pass
    return None

def check_ollama_connection():
    """Check if Ollama is accessible"""
    try:
        response = requests.get(f"{CONFIG['OLLAMA_URL']}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def get_available_models():
    """Get list of available models"""
    try:
        response = requests.get(f"{CONFIG['OLLAMA_URL']}/api/tags", timeout=10)
        if response.status_code == 200:
            return response.json().get("models", [])
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
    return []

# API Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Project Omega - High-Reasoning Uncensored LLM API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=SystemStatus)
async def health():
    """Health check endpoint"""
    ollama_connected = check_ollama_connection()
    models = get_available_models() if ollama_connected else []
    uptime = str(datetime.now() - start_time).split('.')[0]
    
    return SystemStatus(
        status="healthy" if ollama_connected else "degraded",
        ollama_connected=ollama_connected,
        models_available=len(models),
        default_model=CONFIG["DEFAULT_MODEL"],
        gpu_info=get_gpu_info(),
        uptime=uptime
    )

@app.get("/models", response_model=List[Dict[str, Any]])
async def list_models():
    """List available models"""
    try:
        models = get_available_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the LLM"""
    start_time_req = time.time()
    
    try:
        # Configuration
        model = request.model or CONFIG["DEFAULT_MODEL"]
        temperature = request.temperature or CONFIG["TEMPERATURE"]
        max_tokens = request.max_tokens or CONFIG["MAX_TOKENS"]
        top_p = request.top_p or CONFIG["TOP_P"]
        
        # Prepare request
        prompt = request.message
        if request.system_prompt:
            prompt = f"System: {request.system_prompt}\n\nUser: {request.message}"
        
        ollama_request = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            }
        }
        
        logger.info(f"Processing request for model {model}")
        
        # Make request to Ollama
        response = requests.post(
            f"{CONFIG['OLLAMA_URL']}/api/generate",
            json=ollama_request,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            generation_time = time.time() - start_time_req
            
            return ChatResponse(
                response=result["response"],
                model=model,
                timestamp=datetime.now().isoformat(),
                tokens_used=result.get("eval_count"),
                generation_time=round(generation_time, 2)
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Ollama request failed: {response.status_code}"
            )
            
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "uptime": str(datetime.now() - start_time).split('.')[0],
        "config": CONFIG,
        "gpu_info": get_gpu_info(),
        "ollama_connected": check_ollama_connection(),
        "models": len(get_available_models())
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Project Omega API starting up...")
    logger.info(f"Default model: {CONFIG['DEFAULT_MODEL']}")
    logger.info(f"Server: {CONFIG['HOST']}:{CONFIG['PORT']}")
    
    # Check Ollama connection
    if check_ollama_connection():
        models = get_available_models()
        logger.info(f"Ollama connected - {len(models)} models available")
    else:
        logger.warning("Ollama not accessible - check if service is running")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 PROJECT OMEGA - STARTING API SERVER")
    print("High-Reasoning Uncensored LLM API")
    print("="*50)
    print(f"📡 Server: http://{CONFIG['HOST']}:{CONFIG['PORT']}")
    print(f"📚 Documentation: http://{CONFIG['HOST']}:{CONFIG['PORT']}/docs")
    print(f"🔧 Health Check: http://{CONFIG['HOST']}:{CONFIG['PORT']}/health")
    print(f"🤖 Default Model: {CONFIG['DEFAULT_MODEL']}")
    print("="*50 + "\n")
    
    uvicorn.run(
        app, 
        host=CONFIG["HOST"], 
        port=CONFIG["PORT"],
        log_level="info"
    )
