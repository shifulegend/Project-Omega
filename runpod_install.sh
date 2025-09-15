#!/bin/bash

# Project Omega - RunPod Installation Commands
# Copy and paste these commands directly into your RunPod terminal

echo "=== Project Omega Installation Starting ==="
echo "Time: $(date)"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)"
echo ""

# Update system
echo "Updating system..."
apt update && apt upgrade -y

# Install essential packages
echo "Installing essential packages..."
apt install -y python3-pip python3-venv curl wget git htop nvtop unzip

# Install Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
echo "Starting Ollama service..."
systemctl enable ollama
systemctl start ollama

# Wait for Ollama to start
echo "Waiting for Ollama to initialize..."
sleep 10

# Test Ollama
echo "Testing Ollama..."
ollama --version

# Download high-reasoning uncensored models
echo "Downloading Dolphin-Mistral 7B (Uncensored, High Reasoning)..."
ollama pull dolphin-mistral:7b

echo "Downloading WizardLM 13B Uncensored..."
ollama pull wizardlm-uncensored:13b

echo "Downloading CodeLlama 13B Instruct..."
ollama pull codellama:13b-instruct

echo "Downloading Mistral 7B Instruct (alternative)..."
ollama pull mistral:7b-instruct

# List installed models
echo "Installed models:"
ollama list

# Test a model
echo "Testing Dolphin-Mistral model..."
ollama run dolphin-mistral:7b "Hello, can you introduce yourself briefly?"

echo ""
echo "=== Installation Complete! ==="
echo "Primary uncensored model: dolphin-mistral:7b"
echo "High-performance model: wizardlm-uncensored:13b"
echo "Coding specialist: codellama:13b-instruct"
echo ""
echo "Usage examples:"
echo "ollama run dolphin-mistral:7b 'Your prompt here'"
echo "ollama run wizardlm-uncensored:13b 'Complex reasoning task'"
echo "ollama run codellama:13b-instruct 'Write a Python function'"
echo ""
echo "Monitor GPU: watch -n 1 nvidia-smi"
echo "Monitor Ollama: journalctl -u ollama -f"
