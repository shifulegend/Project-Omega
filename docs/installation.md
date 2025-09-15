# Installation Guide - Project Omega

## 📋 Prerequisites

Before installing Project Omega, ensure your system meets the following requirements:

### Hardware Requirements
- **GPU**: NVIDIA RTX 2000 Ada Generation (16GB VRAM) or equivalent
- **RAM**: 16GB+ system memory recommended
- **Storage**: 50GB+ free space for models and dependencies
- **CPU**: Modern multi-core processor (8+ cores recommended)

### Software Requirements
- **OS**: Ubuntu 22.04+ (tested on Ubuntu 22.04 LTS)
- **Python**: 3.11 or higher
- **CUDA**: 12.0 or higher
- **Git**: Latest version
- **Docker**: Optional but recommended

## 🚀 Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/shifulegend/Project-Omega.git
cd Project-Omega

# Make installation script executable
chmod +x scripts/install.sh

# Run the automated installation
bash scripts/install.sh
```

### Method 2: Manual Installation

#### Step 1: System Updates
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-pip python3.11-venv git curl wget
```

#### Step 2: NVIDIA Drivers and CUDA (if not installed)
```bash
# Check if NVIDIA drivers are installed
nvidia-smi

# If not installed, install NVIDIA drivers
sudo apt install -y nvidia-driver-535

# Install CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/cuda-repo-ubuntu2204-12-2-local_12.2.0-535.54.03-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-2-local_12.2.0-535.54.03-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-12-2-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda
```

#### Step 3: Python Environment Setup
```bash
# Create virtual environment
python3.11 -m venv omega_env
source omega_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### Step 4: Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Step 5: Install Additional Dependencies
```bash
pip install -r requirements.txt
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
# Model Configuration
DEFAULT_MODEL=dolphin-mistral:7b
MAX_TOKENS=4096
TEMPERATURE=0.7

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=1

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
GPU_MEMORY_FRACTION=0.9
```

### Model Downloads
```bash
# Download recommended models
ollama pull dolphin-mistral:7b
ollama pull wizardlm-uncensored:13b
ollama pull codellama:13b-instruct
```

## 🧪 Verification

### Test GPU Access
```bash
python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU Count: {torch.cuda.device_count()}'); print(f'GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU"}')"
```

### Test Ollama Installation
```bash
ollama --version
ollama list
```

### Test Model Loading
```bash
ollama run dolphin-mistral:7b "Hello, can you introduce yourself?"
```

## 📊 Post-Installation

### Start Services
```bash
# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Start API server
bash scripts/start_server.sh
```

### Access WebUI (if installed)
Open your browser and navigate to: `http://localhost:8000`

## 🔍 Troubleshooting

### Common Issues

1. **CUDA not detected**
   - Verify NVIDIA drivers: `nvidia-smi`
   - Check CUDA installation: `nvcc --version`
   - Restart system after driver installation

2. **Out of memory errors**
   - Reduce model size or use quantized versions
   - Adjust `GPU_MEMORY_FRACTION` in `.env`
   - Close other GPU applications

3. **Ollama service not starting**
   - Check logs: `journalctl -u ollama`
   - Verify permissions: `sudo chown -R $USER:$USER ~/.ollama`

4. **Python dependencies issues**
   - Update pip: `pip install --upgrade pip`
   - Clear cache: `pip cache purge`
   - Use virtual environment

### Performance Optimization

1. **Memory Management**
   ```bash
   # Set environment variables for optimal performance
   export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
   export CUDA_LAUNCH_BLOCKING=0
   ```

2. **Model Optimization**
   - Use quantized models for better memory efficiency
   - Adjust context length based on available VRAM
   - Enable mixed precision training if supported

## 📚 Next Steps

After successful installation:
1. Review the [Model Selection Guide](models.md)
2. Configure your preferred settings in [Configuration Guide](configuration.md)
3. Explore the [API Usage](api.md) documentation
4. Check [Performance Optimization](optimization.md) tips

---

**Need Help?** Check our [FAQ](faq.md) or open an issue on GitHub.
