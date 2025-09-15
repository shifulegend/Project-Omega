#!/bin/bash

# Project Omega - Automated Installation Script
# Author: MiniMax Agent
# Created: September 15, 2025

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   warn "This script should not be run as root for security reasons."
   warn "Please run as a regular user. The script will use sudo when needed."
   exit 1
fi

log "Starting Project Omega Installation..."

# System Information
info "System Information:"
info "OS: $(lsb_release -d | cut -f2)"
info "Kernel: $(uname -r)"
info "Architecture: $(uname -m)"

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    info "GPU Information:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits
else
    warn "NVIDIA GPU not detected or drivers not installed!"
fi

# Update system
log "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
log "Installing essential packages..."
sudo apt install -y \
    python3.11 \
    python3.11-pip \
    python3.11-venv \
    python3.11-dev \
    git \
    curl \
    wget \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    htop \
    nvtop \
    unzip

# Create Python virtual environment
log "Creating Python virtual environment..."
if [ ! -d "omega_env" ]; then
    python3.11 -m venv omega_env
fi

source omega_env/bin/activate
pip install --upgrade pip setuptools wheel

# Install PyTorch with CUDA support
log "Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Test CUDA availability
log "Testing CUDA availability..."
python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU Count: {torch.cuda.device_count()}'); print(f'GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU"}')"

# Install Ollama
log "Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
else
    info "Ollama already installed"
fi

# Start Ollama service
log "Starting Ollama service..."
sudo systemctl enable ollama || true
sudo systemctl start ollama || true

# Wait for Ollama to start
sleep 5

# Install Python dependencies
log "Installing Python dependencies..."
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
requests==2.31.0
aiohttp==3.9.1
numpy==1.24.3
pandas==2.0.3
matplotlib==3.7.2
seaborn==0.12.2
jupyter==1.0.0
ipywidgets==8.1.1
transformers==4.36.0
accelerate==0.25.0
bitsandbytes==0.42.0
sentencepiece==0.1.99
protobuf==4.25.1
safetensors==0.4.1
huggingface-hub==0.19.4
gradio==4.8.0
streamlit==1.29.0
openai==1.3.7
anthropics==0.7.8
langchain==0.0.350
langchain-community==0.0.1
chromadb==0.4.18
psutil==5.9.6
gputil==1.4.0
pynvml==11.5.0
click==8.1.7
rich==13.7.0
pyaml==6.0.1
python-dotenv==1.0.0
EOF

pip install -r requirements.txt

# Download recommended models
log "Downloading recommended LLM models..."
log "This may take a while depending on your internet connection..."

# Download Dolphin Mistral 7B (Uncensored, High Reasoning)
log "Downloading Dolphin-Mistral 7B (Uncensored)..."
ollama pull dolphin-mistral:7b

# Download WizardLM 13B Uncensored (if enough VRAM)
log "Downloading WizardLM 13B Uncensored..."
ollama pull wizardlm-uncensored:13b || warn "WizardLM 13B download failed - may require more VRAM"

# Download CodeLlama for coding tasks
log "Downloading CodeLlama 13B Instruct..."
ollama pull codellama:13b-instruct || warn "CodeLlama 13B download failed - may require more VRAM"

# Download smaller alternative models
log "Downloading alternative models..."
ollama pull mistral:7b-instruct
ollama pull openchat:7b

# Create configuration files
log "Creating configuration files..."

# Create .env file
cat > .env << EOF
# Project Omega Configuration
# Created: $(date)

# Model Configuration
DEFAULT_MODEL=dolphin-mistral:7b
MAX_TOKENS=4096
TEMPERATURE=0.7
TOP_P=0.9
TOP_K=40
REPEAT_PENALTY=1.1

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=1
TIMEOUT=300

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
GPU_MEMORY_FRACTION=0.9
MIXED_PRECISION=true

# Security
API_KEY=omega-$(openssl rand -hex 16)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/omega.log

# Model Paths
MODEL_CACHE_DIR=~/.ollama/models
HUGGINGFACE_CACHE_DIR=~/.cache/huggingface
EOF

# Create directories
mkdir -p logs
mkdir -p data
mkdir -p models
mkdir -p backups

# Create start server script
cat > scripts/start_server.sh << 'EOF'
#!/bin/bash

# Project Omega - Server Startup Script

set -e

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate virtual environment
source omega_env/bin/activate

# Start Ollama service
echo "Starting Ollama service..."
sudo systemctl start ollama

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
sleep 5

# Check if default model is available
echo "Checking default model: $DEFAULT_MODEL"
if ! ollama list | grep -q "$DEFAULT_MODEL"; then
    echo "Default model not found. Available models:"
    ollama list
    echo "Please set DEFAULT_MODEL in .env to an available model"
    exit 1
fi

# Start the API server
echo "Starting Project Omega API server..."
echo "Server will be available at: http://$API_HOST:$API_PORT"

# Check if main.py exists, if not create a simple one
if [ ! -f "main.py" ]; then
    echo "Creating basic API server..."
    cat > main.py << 'PYEOF'
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Project Omega API", version="1.0.0")

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: Optional[int] = None

@app.get("/")
async def root():
    return {"message": "Project Omega API", "status": "active"}

@app.get("/health")
async def health():
    try:
        # Test Ollama connection
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {"status": "healthy", "ollama": "connected", "models": len(models)}
        else:
            return {"status": "unhealthy", "ollama": "disconnected"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        model = request.model or os.getenv("DEFAULT_MODEL", "dolphin-mistral:7b")
        temperature = request.temperature or float(os.getenv("TEMPERATURE", 0.7))
        max_tokens = request.max_tokens or int(os.getenv("MAX_TOKENS", 4096))
        
        ollama_request = {
            "model": model,
            "prompt": request.message,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=ollama_request,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            return ChatResponse(
                response=result["response"],
                model=model,
                tokens_used=result.get("eval_count")
            )
        else:
            raise HTTPException(status_code=500, detail="Ollama request failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch models")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYEOF
fi

# Start the server
python main.py
EOF

chmod +x scripts/start_server.sh

# Create model management script
cat > scripts/manage_models.sh << 'EOF'
#!/bin/bash

# Project Omega - Model Management Script

show_usage() {
    echo "Usage: $0 [list|pull|remove|info] [model_name]"
    echo "Commands:"
    echo "  list                 - List all installed models"
    echo "  pull <model>         - Download a new model"
    echo "  remove <model>       - Remove an installed model"
    echo "  info <model>         - Show model information"
    echo "  recommended          - Show recommended models for this GPU"
}

if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

case $1 in
    list)
        echo "Installed models:"
        ollama list
        ;;
    pull)
        if [ -z "$2" ]; then
            echo "Error: Model name required"
            show_usage
            exit 1
        fi
        echo "Downloading model: $2"
        ollama pull "$2"
        ;;
    remove)
        if [ -z "$2" ]; then
            echo "Error: Model name required"
            show_usage
            exit 1
        fi
        echo "Removing model: $2"
        ollama rm "$2"
        ;;
    info)
        if [ -z "$2" ]; then
            echo "Error: Model name required"
            show_usage
            exit 1
        fi
        ollama show "$2"
        ;;
    recommended)
        echo "Recommended models for RTX 2000 Ada Generation (16GB VRAM):"
        echo ""
        echo "High Priority (Uncensored & High Reasoning):"
        echo "  - dolphin-mistral:7b      (8GB VRAM, Uncensored)"
        echo "  - wizardlm-uncensored:13b (14GB VRAM, Uncensored)"
        echo ""
        echo "Alternative Models:"
        echo "  - codellama:13b-instruct  (14GB VRAM, Coding)"
        echo "  - mistral:7b-instruct     (8GB VRAM, General)"
        echo "  - openchat:7b             (8GB VRAM, Fast)"
        echo ""
        echo "To install: ./scripts/manage_models.sh pull <model_name>"
        ;;
    *)
        echo "Error: Unknown command '$1'"
        show_usage
        exit 1
        ;;
esac
EOF

chmod +x scripts/manage_models.sh

# Create monitoring script
cat > scripts/monitor.sh << 'EOF'
#!/bin/bash

# Project Omega - System Monitoring Script

watch -n 2 '
echo "=== Project Omega System Monitor ==="
echo "Time: $(date)"
echo ""

echo "=== GPU Status ==="
nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits | while read line; do
    echo "GPU: $line"
done
echo ""

echo "=== System Resources ==="
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk "{print \$2}" | cut -d"%" -f1)%"
echo "Memory: $(free -h | grep Mem | awk "{print \$3\"/\"\$2}")"
echo "Disk: $(df -h / | tail -1 | awk "{print \$3\"/\"\$2\" (\"\$5\" used)}")  "
echo ""

echo "=== Ollama Status ==="
if systemctl is-active --quiet ollama; then
    echo "Ollama Service: Running"
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "Ollama API: Accessible"
        echo "Models: $(curl -s http://localhost:11434/api/tags | jq ".models | length" 2>/dev/null || echo "N/A")"
    else
        echo "Ollama API: Not accessible"
    fi
else
    echo "Ollama Service: Not running"
fi
echo ""

echo "=== Active Processes ==="
ps aux | grep -E "ollama|python|uvicorn" | grep -v grep | head -5
'
EOF

chmod +x scripts/monitor.sh

# Create backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash

# Project Omega - Backup Script

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

echo "Creating backup in: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup configuration files
cp .env "$BACKUP_DIR/" 2>/dev/null || true
cp requirements.txt "$BACKUP_DIR/" 2>/dev/null || true
cp -r scripts "$BACKUP_DIR/" 2>/dev/null || true
cp -r docs "$BACKUP_DIR/" 2>/dev/null || true

# Backup logs
cp -r logs "$BACKUP_DIR/" 2>/dev/null || true

# List installed models
ollama list > "$BACKUP_DIR/installed_models.txt" 2>/dev/null || true

# System information
echo "System backup created on: $(date)" > "$BACKUP_DIR/backup_info.txt"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)" >> "$BACKUP_DIR/backup_info.txt"
echo "CUDA Version: $(nvcc --version | grep release | awk '{print $6}')" >> "$BACKUP_DIR/backup_info.txt" 2>/dev/null || true
echo "Python Version: $(python3 --version)" >> "$BACKUP_DIR/backup_info.txt"
echo "Ollama Version: $(ollama --version)" >> "$BACKUP_DIR/backup_info.txt" 2>/dev/null || true

echo "Backup completed: $BACKUP_DIR"
echo "Backup size: $(du -sh $BACKUP_DIR | cut -f1)"
EOF

chmod +x scripts/backup.sh

# Test installation
log "Testing installation..."

# Test Python environment
log "Testing Python environment..."
python3 -c "import torch, transformers, fastapi; print('Core packages imported successfully')"

# Test CUDA
if python3 -c "import torch; assert torch.cuda.is_available(), 'CUDA not available'"; then
    log "CUDA test passed"
else
    warn "CUDA test failed - GPU acceleration may not work"
fi

# Test Ollama
log "Testing Ollama..."
if ollama list &>/dev/null; then
    log "Ollama test passed"
    info "Available models:"
    ollama list
else
    warn "Ollama test failed"
fi

# Create desktop shortcut (optional)
if [ -d "$HOME/Desktop" ]; then
    cat > "$HOME/Desktop/Project-Omega.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Project Omega
Comment=High-Reasoning Uncensored LLM
Exec=gnome-terminal --working-directory="$(pwd)" --command="bash scripts/start_server.sh"
Icon=applications-science
Terminal=false
Categories=Development;Science;
EOF
    chmod +x "$HOME/Desktop/Project-Omega.desktop"
    log "Desktop shortcut created"
fi

# Final setup summary
log "Installation completed successfully!"
echo ""
info "=== Project Omega Installation Summary ==="
info "Location: $(pwd)"
info "Python Environment: $(pwd)/omega_env"
info "Configuration: $(pwd)/.env"
info "Available Models:"
ollama list | tail -n +2
echo ""
info "=== Next Steps ==="
info "1. Review configuration in .env file"
info "2. Start the server: bash scripts/start_server.sh"
info "3. Access API at: http://localhost:8000"
info "4. Monitor system: bash scripts/monitor.sh"
info "5. Manage models: bash scripts/manage_models.sh"
echo ""
info "=== Useful Commands ==="
info "Start server:    bash scripts/start_server.sh"
info "Monitor system:  bash scripts/monitor.sh"
info "Manage models:   bash scripts/manage_models.sh"
info "Create backup:   bash scripts/backup.sh"
info "View logs:       tail -f logs/omega.log"
echo ""
log "Project Omega is ready! 🚀"
