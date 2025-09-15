# Project Omega - High-Reasoning Uncensored LLM Deployment

![Project Status](https://img.shields.io/badge/Status-Active-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![CUDA](https://img.shields.io/badge/CUDA-Compatible-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Overview

Project Omega is a comprehensive deployment solution for high-reasoning uncensored Large Language Models (LLMs) optimized for GPU environments. This project provides complete documentation, installation scripts, and configuration files for deploying powerful AI models on cloud instances.

## 🎯 Features

- **High-Reasoning Models**: Carefully selected LLMs optimized for complex reasoning tasks
- **Uncensored Operation**: Models fine-tuned for unrestricted conversations
- **GPU Optimized**: Configured for NVIDIA RTX 2000 Ada Generation (16GB VRAM)
- **Easy Deployment**: One-click installation scripts
- **Comprehensive Documentation**: Complete setup and usage guides
- **Multiple Frameworks**: Support for Ollama, vLLM, and Text Generation WebUI

## 📋 System Requirements

- **GPU**: NVIDIA RTX 2000 Ada Generation (16GB VRAM) or similar
- **RAM**: 16GB+ system memory
- **Storage**: 50GB+ available space
- **OS**: Ubuntu 22.04+ or compatible Linux distribution
- **Python**: 3.11+
- **CUDA**: 12.0+

## 🔧 Quick Start

```bash
# Clone the repository
git clone https://github.com/shifulegend/Project-Omega.git
cd Project-Omega

# Run the installation script
bash scripts/install.sh

# Start the model server
bash scripts/start_server.sh
```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Model Selection Guide](docs/models.md)
- [Configuration Guide](docs/configuration.md)
- [API Usage](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Performance Optimization](docs/optimization.md)

## 🤖 Supported Models

| Model | Size | VRAM Required | Reasoning Score | Uncensored |
|-------|------|---------------|----------------|------------|
| Dolphin-2.6-Mistral-7B | 7B | ~8GB | ⭐⭐⭐⭐⭐ | ✅ |
| WizardLM-13B-Uncensored | 13B | ~14GB | ⭐⭐⭐⭐⭐ | ✅ |
| CodeLlama-13B-Instruct | 13B | ~14GB | ⭐⭐⭐⭐⭐ | ⚠️ |
| Mistral-7B-Instruct | 7B | ~8GB | ⭐⭐⭐⭐ | ⚠️ |

## 🛠️ Architecture

```
Project Omega
├── Frontend (Optional WebUI)
├── API Server (FastAPI/Flask)
├── Model Server (Ollama/vLLM)
└── Storage (Models & Configs)
```

## 📊 Performance Benchmarks

*Performance metrics will be updated after installation and testing*

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This project is for educational and research purposes. Users are responsible for ensuring compliance with applicable laws and regulations when using uncensored AI models.

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check our [FAQ](docs/faq.md)
- Review the [troubleshooting guide](docs/troubleshooting.md)

---

**Author**: MiniMax Agent  
**Created**: September 15, 2025  
**Last Updated**: September 15, 2025
