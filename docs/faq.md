# Frequently Asked Questions (FAQ) - Project Omega

## 🔍 General Questions

### Q: What is Project Omega?
A: Project Omega is a comprehensive deployment solution for high-reasoning uncensored Large Language Models (LLMs). It provides easy installation, configuration, and management of powerful AI models optimized for GPU environments.

### Q: Why "uncensored" models?
A: Uncensored models have had safety filters and content restrictions removed, allowing for more open and unrestricted conversations. This is useful for research, creative writing, and scenarios where content filtering might be limiting.

### Q: Is this legal to use?
A: The software itself is legal. However, users are responsible for ensuring their use complies with local laws and regulations. Some content generation may be restricted in certain jurisdictions.

## 💻 Technical Questions

### Q: What hardware do I need?
A: Minimum requirements:
- NVIDIA GPU with 8GB+ VRAM (16GB recommended)
- 16GB+ system RAM
- 50GB+ storage space
- Ubuntu 22.04+ or compatible Linux distribution

### Q: Can I run this on other GPUs?
A: Currently optimized for NVIDIA GPUs with CUDA support. AMD GPUs with ROCm support may work but are not officially tested.

### Q: How much VRAM do different models need?
- 7B models: ~8GB VRAM
- 13B models: ~14GB VRAM
- 20B+ models: 20GB+ VRAM (not supported on RTX 2000)

### Q: Can I run multiple models simultaneously?
A: With 16GB VRAM, you can typically run one 13B model OR multiple smaller 7B models. Configure `OLLAMA_MAX_LOADED_MODELS` in your environment.

## 🚀 Installation & Setup

### Q: The installation script failed. What should I do?
A: Common solutions:
1. Check internet connection
2. Ensure sufficient disk space (50GB+)
3. Verify NVIDIA drivers: `nvidia-smi`
4. Run with verbose output: `bash -x scripts/install.sh`
5. Check logs in `logs/` directory

### Q: Ollama service won't start
A: Try these steps:
```bash
# Check service status
sudo systemctl status ollama

# Restart service
sudo systemctl restart ollama

# Check logs
journalctl -u ollama -f

# Manual start
ollama serve
```

### Q: CUDA is not detected
A: Verify CUDA installation:
```bash
# Check NVIDIA drivers
nvidia-smi

# Check CUDA version
nvcc --version

# Test PyTorch CUDA
python3 -c "import torch; print(torch.cuda.is_available())"
```

### Q: Python dependencies fail to install
A: Solutions:
```bash
# Update pip
pip install --upgrade pip

# Clear cache
pip cache purge

# Install with verbose output
pip install -v package_name

# Use conda instead
conda install package_name
```

## 🔧 Configuration & Usage

### Q: How do I change the default model?
A: Edit the `.env` file:
```bash
DEFAULT_MODEL=your-preferred-model
```
Or specify in API requests:
```json
{"message": "Hello", "model": "dolphin-mistral:7b"}
```

### Q: How do I adjust response quality vs speed?
A: Modify these parameters in `.env`:
```bash
# Higher quality, slower
TEMPERATURE=0.3
TOP_P=0.8
MAX_TOKENS=4096

# Faster, less detailed
TEMPERATURE=0.8
TOP_P=0.95
MAX_TOKENS=2048
```

### Q: Can I access the API remotely?
A: Yes, modify the API host in `.env`:
```bash
API_HOST=0.0.0.0  # Allow external access
API_PORT=8000
```
**Security Note**: Implement authentication for production use.

### Q: How do I add API authentication?
A: The system includes a basic API key. Check `.env` for:
```bash
API_KEY=omega-[random-string]
```
Implement proper authentication in production environments.

## 📈 Performance & Optimization

### Q: My responses are very slow. How can I speed them up?
A: Try these optimizations:
1. Use smaller models (7B instead of 13B)
2. Reduce context length
3. Lower temperature and top_p values
4. Ensure GPU isn't thermal throttling
5. Close other GPU applications

### Q: I'm getting "Out of Memory" errors
A: Solutions:
```bash
# Switch to smaller model
ollama pull mistral:7b-instruct

# Reduce context in .env
MAX_TOKENS=2048

# Monitor GPU memory
watch -n 1 nvidia-smi

# Restart Ollama service
sudo systemctl restart ollama
```

### Q: How do I monitor system performance?
A: Use the built-in monitoring script:
```bash
bash scripts/monitor.sh
```
Or individual commands:
```bash
# GPU monitoring
nvidia-smi
watch -n 1 nvidia-smi

# System resources
htop
top

# Disk usage
df -h
du -sh ~/.ollama/models/
```

## 💾 Model Management

### Q: How do I download new models?
A: Use the model management script:
```bash
# List available models
bash scripts/manage_models.sh list

# Download new model
bash scripts/manage_models.sh pull model-name

# Direct Ollama command
ollama pull model-name
```

### Q: How do I remove models to free space?
A: Remove unused models:
```bash
# Remove specific model
bash scripts/manage_models.sh remove model-name

# Direct Ollama command
ollama rm model-name

# List models with sizes
ollama list
```

### Q: Where are models stored?
A: Default locations:
- **Linux**: `~/.ollama/models/`
- **Config**: `~/.ollama/`
- **Logs**: `~/logs/` (Project Omega)

### Q: Can I use custom models?
A: Yes, you can:
1. Import GGUF models: `ollama create mymodel -f Modelfile`
2. Pull from Hugging Face: Use compatible model names
3. Create custom Modelfiles for specific configurations

## 🔒 Security & Safety

### Q: Are uncensored models safe to use?
A: Uncensored models can generate unrestricted content. Use responsibly:
- Implement your own content filtering if needed
- Monitor usage and outputs
- Ensure compliance with local laws
- Consider the context and audience

### Q: How do I implement content filtering?
A: You can add filtering at the API level:
```python
# Example post-processing filter
def filter_response(text):
    # Implement your filtering logic
    if contains_inappropriate_content(text):
        return "Content filtered"
    return text
```

### Q: Can I audit model conversations?
A: Yes, enable logging in `.env`:
```bash
LOG_LEVEL=INFO
LOG_FILE=logs/conversations.log
```

## 🔄 Updates & Maintenance

### Q: How do I update Project Omega?
A: Update from the repository:
```bash
cd Project-Omega
git pull origin main
bash scripts/install.sh  # If needed
```

### Q: How do I update models?
A: Models update automatically when pulling:
```bash
ollama pull model-name  # Gets latest version
```

### Q: How do I backup my configuration?
A: Use the backup script:
```bash
bash scripts/backup.sh
```
This saves:
- Configuration files
- Model list
- Logs
- System information

## 🐛 Troubleshooting

### Q: The API returns 500 errors
A: Check these common causes:
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Check model availability
ollama list

# Review API logs
tail -f logs/omega.log

# Restart services
sudo systemctl restart ollama
bash scripts/start_server.sh
```

### Q: Model responses are inconsistent
A: This could be due to:
- High temperature settings (try 0.7 or lower)
- Insufficient context
- Model-specific behavior
- Hardware thermal throttling

### Q: Installation takes too long
A: Model downloads can be slow:
- Use stable internet connection
- Download smaller models first
- Use `wget` or `curl` with resume capability
- Consider using model mirrors

## 📞 Getting Help

### Q: Where can I get additional support?
A: Multiple support channels:
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive guides in `docs/`
- **Community**: Join discussions on relevant forums
- **Logs**: Check `logs/` directory for error details

### Q: How do I report a bug?
A: When reporting issues, include:
1. System information (GPU, OS, CUDA version)
2. Error messages and logs
3. Steps to reproduce
4. Expected vs actual behavior
5. Configuration files (without sensitive data)

### Q: Can I contribute to the project?
A: Absolutely! Contributions welcome:
- Bug fixes and improvements
- Documentation updates
- New model configurations
- Performance optimizations
- Testing on different hardware

---

**Still need help?** Check the [Troubleshooting Guide](troubleshooting.md) or open an issue on GitHub.
