# Project Omega - RunPod Quick Start Guide

## 🚀 Installation Instructions

### Step 1: Basic Setup
Copy and paste these commands in your RunPod terminal:

```bash
# Update system
apt update && apt upgrade -y

# Install essential packages
apt install -y python3-pip python3-venv curl wget git htop nvtop unzip

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
systemctl enable ollama
systemctl start ollama

# Wait for Ollama to initialize
sleep 10
```

### Step 2: Download High-Reasoning Uncensored Models

```bash
# Primary uncensored model (recommended)
echo "Downloading Dolphin-Mistral 7B (Uncensored)..."
ollama pull dolphin-mistral:7b

# High-performance uncensored model
echo "Downloading WizardLM 13B Uncensored..."
ollama pull wizardlm-uncensored:13b

# Coding specialist
echo "Downloading CodeLlama 13B Instruct..."
ollama pull codellama:13b-instruct

# Alternative fast model
echo "Downloading Mistral 7B Instruct..."
ollama pull mistral:7b-instruct
```

### Step 3: Verify Installation

```bash
# Check installed models
ollama list

# Test the primary model
ollama run dolphin-mistral:7b "Hello, introduce yourself briefly"

# Check GPU usage
nvidia-smi
```

### Step 4: Download API Server

```bash
# Download the API server
wget https://raw.githubusercontent.com/shifulegend/Project-Omega/main/api_server.py

# Install Python dependencies
pip install fastapi uvicorn requests pydantic

# Start API server
python3 api_server.py
```

## 🎯 Usage Examples

### Command Line Usage

```bash
# Basic chat with uncensored model
ollama run dolphin-mistral:7b "Explain quantum computing in simple terms"

# Complex reasoning with 13B model
ollama run wizardlm-uncensored:13b "Analyze the philosophical implications of artificial consciousness"

# Coding assistance
ollama run codellama:13b-instruct "Write a Python function to implement a binary search tree"
```

### API Usage

Once the API server is running, you can use it via HTTP:

```bash
# Test API health
curl http://localhost:8000/health

# Chat via API
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you help me with?",
    "model": "dolphin-mistral:7b",
    "temperature": 0.7
  }'
```

### Web Interface

Access the interactive documentation at: `http://your-runpod-ip:8000/docs`

## 📊 Model Recommendations

### For Maximum Uncensored Performance:
- **Primary**: `dolphin-mistral:7b` (8GB VRAM)
- **Secondary**: `wizardlm-uncensored:13b` (14GB VRAM)

### For Coding Tasks:
- **Primary**: `codellama:13b-instruct`
- **Alternative**: `dolphin-codellama:7b`

### For Fast Responses:
- **Primary**: `mistral:7b-instruct`
- **Alternative**: `openchat:7b`

## 🔧 Configuration Options

### Environment Variables
Create a `.env` file:

```bash
cat > .env << EOF
# Model Configuration
DEFAULT_MODEL=dolphin-mistral:7b
MAX_TOKENS=4096
TEMPERATURE=0.7
TOP_P=0.9

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
GPU_MEMORY_FRACTION=0.9
EOF
```

## 📈 Monitoring

### GPU Monitoring
```bash
# Real-time GPU monitoring
watch -n 1 nvidia-smi

# Or use nvtop for better interface
nvtop
```

### Ollama Monitoring
```bash
# Check Ollama service status
systemctl status ollama

# View Ollama logs
journalctl -u ollama -f

# Check running models
ollama ps
```

## 🛠️ Troubleshooting

### Common Issues

1. **Ollama not starting**:
   ```bash
   systemctl restart ollama
   journalctl -u ollama -f
   ```

2. **Out of memory**:
   ```bash
   # Switch to smaller model
   ollama run mistral:7b-instruct
   
   # Or reduce context length
   export OLLAMA_MAX_LOADED_MODELS=1
   ```

3. **API not accessible**:
   ```bash
   # Check if port is open
   netstat -tulpn | grep :8000
   
   # Restart API server
   python3 api_server.py
   ```

## 🔗 Access URLs

- **API Endpoint**: `http://your-runpod-ip:8000`
- **Documentation**: `http://your-runpod-ip:8000/docs`
- **Health Check**: `http://your-runpod-ip:8000/health`
- **Models List**: `http://your-runpod-ip:8000/models`

## 🎉 Success Indicators

✅ Ollama service running: `systemctl is-active ollama`  
✅ Models downloaded: `ollama list` shows your models  
✅ GPU detected: `nvidia-smi` shows your RTX 2000  
✅ API responding: `curl http://localhost:8000/health` returns status  
✅ Model responding: Test chat returns coherent response  

---

**🚀 You're now ready to use high-reasoning uncensored LLMs on your RunPod instance!**

For more advanced configuration, check the full documentation at:
https://github.com/shifulegend/Project-Omega
