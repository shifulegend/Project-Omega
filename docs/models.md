# Model Selection Guide - Project Omega

## 🤖 Overview

This guide helps you select the optimal Large Language Model (LLM) for your specific needs, considering your hardware constraints and use case requirements.

## 📋 Hardware Considerations

### RTX 2000 Ada Generation (16GB VRAM)

Your GPU configuration allows for the following model categories:

- **7B Models**: Comfortable fit with room for context
- **13B Models**: Tight fit, may require optimization
- **20B+ Models**: Not recommended (insufficient VRAM)

## 🎯 Recommended Models

### Tier 1: High-Reasoning Uncensored (Primary Recommendations)

#### 1. Dolphin-2.6-Mistral-7B
- **Size**: 7B parameters (~8GB VRAM)
- **Strengths**: Highly uncensored, excellent reasoning, ethical guidelines removed
- **Use Cases**: Open-ended conversations, creative writing, unrestricted Q&A
- **Installation**: `ollama pull dolphin-mistral:7b`
- **Rating**: ⭐⭐⭐⭐⭐

#### 2. WizardLM-13B-Uncensored
- **Size**: 13B parameters (~14GB VRAM)
- **Strengths**: Superior reasoning capabilities, uncensored responses
- **Use Cases**: Complex problem solving, detailed analysis, research assistance
- **Installation**: `ollama pull wizardlm-uncensored:13b`
- **Rating**: ⭐⭐⭐⭐⭐
- **Note**: May require memory optimization for 16GB VRAM

### Tier 2: Specialized High-Performance

#### 3. CodeLlama-13B-Instruct
- **Size**: 13B parameters (~14GB VRAM)
- **Strengths**: Exceptional coding abilities, technical reasoning
- **Use Cases**: Programming, code review, technical documentation
- **Installation**: `ollama pull codellama:13b-instruct`
- **Rating**: ⭐⭐⭐⭐⭐
- **Censorship**: Moderate (technical focus)

#### 4. Dolphin-2.6-CodeLlama-7B
- **Size**: 7B parameters (~8GB VRAM)
- **Strengths**: Coding + uncensored combination
- **Use Cases**: Unrestricted coding assistance, technical problem solving
- **Installation**: `ollama pull dolphin-codellama:7b`
- **Rating**: ⭐⭐⭐⭐

### Tier 3: Fast & Efficient Alternatives

#### 5. Mistral-7B-Instruct
- **Size**: 7B parameters (~8GB VRAM)
- **Strengths**: Fast inference, good general capabilities
- **Use Cases**: Quick responses, general chat, balanced performance
- **Installation**: `ollama pull mistral:7b-instruct`
- **Rating**: ⭐⭐⭐⭐
- **Censorship**: Light to moderate

#### 6. OpenChat-7B
- **Size**: 7B parameters (~8GB VRAM)
- **Strengths**: Very fast, optimized for conversation
- **Use Cases**: Real-time chat, quick Q&A
- **Installation**: `ollama pull openchat:7b`
- **Rating**: ⭐⭐⭐

## 📀 Model Comparison Matrix

| Model | Size | VRAM | Reasoning | Uncensored | Speed | Coding |
|-------|------|------|-----------|------------|-------|--------|
| Dolphin-Mistral-7B | 7B | 8GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| WizardLM-13B-Uncensored | 13B | 14GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| CodeLlama-13B-Instruct | 13B | 14GB | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Dolphin-CodeLlama-7B | 7B | 8GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Mistral-7B-Instruct | 7B | 8GB | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| OpenChat-7B | 7B | 8GB | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## 🚀 Installation Commands

### Quick Install - Recommended Set
```bash
# Primary uncensored models
ollama pull dolphin-mistral:7b
ollama pull wizardlm-uncensored:13b

# Coding specialist
ollama pull codellama:13b-instruct

# Fast alternatives
ollama pull mistral:7b-instruct
ollama pull openchat:7b
```

### Individual Installation
```bash
# Replace <model-name> with desired model
ollama pull <model-name>

# Examples:
ollama pull dolphin-mistral:7b
ollama pull wizardlm-uncensored:13b
```

## 📈 Performance Optimization

### Memory Management

#### For 13B Models on 16GB VRAM:
```bash
# Set memory optimization
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_QUEUE=10
```

#### Context Length Optimization:
- **7B Models**: Up to 8K context
- **13B Models**: 4K-6K context recommended

### Quality vs Speed Trade-offs

#### Maximum Quality:
```bash
# Use 13B models with higher context
# Temperature: 0.3-0.7
# Top-p: 0.8-0.95
```

#### Balanced Performance:
```bash
# Use 7B models with moderate settings
# Temperature: 0.7
# Top-p: 0.9
```

#### Maximum Speed:
```bash
# Use OpenChat or Mistral 7B
# Lower context length (2K-4K)
# Temperature: 0.5-0.8
```

## 🗺 Use Case Mapping

### Creative Writing & Storytelling
- **Primary**: Dolphin-Mistral-7B
- **Alternative**: WizardLM-13B-Uncensored

### Code Development
- **Primary**: CodeLlama-13B-Instruct
- **Alternative**: Dolphin-CodeLlama-7B

### Research & Analysis
- **Primary**: WizardLM-13B-Uncensored
- **Alternative**: Dolphin-Mistral-7B

### General Chat & Q&A
- **Primary**: Dolphin-Mistral-7B
- **Alternative**: Mistral-7B-Instruct

### Real-time Applications
- **Primary**: OpenChat-7B
- **Alternative**: Mistral-7B-Instruct

## ⚠️ Important Considerations

### Uncensored Models
- **Responsibility**: Use ethically and legally
- **Content Filtering**: Implement your own if needed
- **Legal Compliance**: Ensure compliance with local laws

### Hardware Limitations
- **VRAM Monitoring**: Use `nvidia-smi` to monitor usage
- **Temperature**: Monitor GPU temperature during heavy use
- **Cooling**: Ensure adequate cooling for sustained workloads

## 🔄 Model Switching

### Runtime Model Switching
```bash
# Via API
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "dolphin-mistral:7b"}'

# Via Ollama CLI
ollama run dolphin-mistral:7b "Your prompt here"
```

### Default Model Configuration
```bash
# Edit .env file
DEFAULT_MODEL=dolphin-mistral:7b
```

## 🔍 Troubleshooting

### Common Issues

1. **Out of Memory (OOM)**
   - Switch to smaller model (13B → 7B)
   - Reduce context length
   - Lower batch size

2. **Slow Response Times**
   - Use 7B models instead of 13B
   - Optimize system settings
   - Check GPU utilization

3. **Model Not Loading**
   - Verify model is downloaded: `ollama list`
   - Check available space: `df -h`
   - Restart Ollama service

### Performance Tuning

```bash
# Check current usage
nvidia-smi

# Monitor real-time usage
watch -n 1 nvidia-smi

# Check Ollama logs
journalctl -u ollama -f
```

## 📚 Additional Resources

- [Ollama Model Library](https://ollama.ai/library)
- [Hugging Face Model Hub](https://huggingface.co/models)
- [Model Performance Benchmarks](benchmarks.md)
- [API Configuration Guide](api.md)

---

**Next Steps**: After selecting your models, proceed to the [Configuration Guide](configuration.md) for optimal setup.
