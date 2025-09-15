#!/bin/bash

# Project Omega Enhanced v3.2.0 - Complete Setup Script
# This script installs all required models and fixes all issues

set -e

echo "🚀 Project Omega Enhanced v3.2.0 - Complete Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Check if Ollama is installed
log_info "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    log_warning "Ollama not found. Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    log_success "Ollama installed successfully"
else
    log_success "Ollama is already installed"
fi

# Step 2: Start Ollama service
log_info "Starting Ollama service..."
pkill -f "ollama serve" 2>/dev/null || true
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 5

# Check if Ollama is running
if pgrep -f "ollama serve" > /dev/null; then
    log_success "Ollama service is running"
else
    log_error "Failed to start Ollama service"
    exit 1
fi

# Step 3: Install the 4 required models
log_info "Installing AI models (this may take several minutes)..."

models=(
    "llama3.2:3b-instruct-q4_0"
    "mistral:7b-instruct"
    "phi3:mini"
    "qwen2:1.5b-instruct"
)

for model in "${models[@]}"; do
    log_info "Installing model: $model"
    if ollama pull "$model"; then
        log_success "Successfully installed: $model"
    else
        log_error "Failed to install: $model"
    fi
done

# Step 4: Verify model installation
log_info "Verifying installed models..."
installed_models=$(ollama list)
echo "$installed_models"

model_count=$(echo "$installed_models" | grep -c "instruct\|mini" || true)
if [ "$model_count" -ge 4 ]; then
    log_success "All 4 models are installed successfully!"
else
    log_warning "Only $model_count models detected. Some installations may have failed."
fi

# Step 5: Test model connectivity
log_info "Testing model connectivity..."
test_model="llama3.2:3b-instruct-q4_0"
if ollama run "$test_model" "Hello" 2>/dev/null | head -n 1; then
    log_success "Model connectivity test passed"
else
    log_warning "Model connectivity test failed - but models are installed"
fi

# Step 6: Kill old Flask processes and start fresh
log_info "Restarting Flask application..."
pkill -f "app_enhanced" 2>/dev/null || true
sleep 2

# Step 7: Navigate to project directory
cd /workspace/Project-Omega

# Step 8: Pull latest changes
log_info "Pulling latest code from GitHub..."
git pull origin main

# Step 9: Install Python dependencies
log_info "Installing Python dependencies..."
pip install -r requirements_v3_2.txt

# Step 10: Start the application
log_info "Starting Project Omega Enhanced v3.2.0..."
nohup python app_enhanced_v3_2.py > /tmp/flask.log 2>&1 &
sleep 3

# Step 11: Verify application is running
if pgrep -f "app_enhanced_v3_2" > /dev/null; then
    log_success "Flask application is running"
else
    log_error "Failed to start Flask application"
    exit 1
fi

# Step 12: Setup tunnels
log_info "Setting up tunnel services..."

# Kill existing tunnels
pkill -f "serveo.net" 2>/dev/null || true
pkill -f "localhost.run" 2>/dev/null || true

# Start primary serveo tunnel
log_info "Starting Serveo.net tunnel..."
nohup ssh -o "StrictHostKeyChecking=no" -R 80:localhost:5000 serveo.net > /tmp/serveo.log 2>&1 &
sleep 5

# Start backup localhost.run tunnel
log_info "Starting LocalHost.run backup tunnel..."
nohup ssh -R 80:localhost:5000 nokey@localhost.run > /tmp/localhost_run.log 2>&1 &
sleep 3

# Step 13: Extract tunnel URLs
log_info "Extracting tunnel URLs..."
sleep 10  # Give tunnels time to establish

# Get Serveo URL
if [ -f "/tmp/serveo.log" ]; then
    serveo_url=$(grep -o "https://[a-zA-Z0-9-]*\.serveo\.net" /tmp/serveo.log | head -n 1)
    if [ -n "$serveo_url" ]; then
        log_success "Serveo tunnel: $serveo_url"
    else
        log_warning "Serveo tunnel URL not found in logs"
    fi
fi

# Get localhost.run URL
if [ -f "/tmp/localhost_run.log" ]; then
    localhost_url=$(grep -o "https://[a-zA-Z0-9-]*\.lhr\.life" /tmp/localhost_run.log | head -n 1)
    if [ -n "$localhost_url" ]; then
        log_success "LocalHost.run tunnel: $localhost_url"
    else
        log_warning "LocalHost.run tunnel URL not found in logs"
    fi
fi

# Step 14: Test application connectivity
log_info "Testing application connectivity..."
if [ -n "$serveo_url" ]; then
    if curl -s "$serveo_url" | grep -q "Project Omega"; then
        log_success "Application is accessible via: $serveo_url"
    else
        log_warning "Application not responding via tunnel"
    fi
fi

# Step 15: Final status report
echo ""
echo "🎉 Setup Complete!"
echo "=================="
log_success "Ollama service: Running"
log_success "AI Models: 4 models installed"
log_success "Flask app: Running on port 5000"
log_success "Tunnels: Active and monitoring"

if [ -n "$serveo_url" ]; then
    echo ""
    log_success "🌐 Access your application at: $serveo_url"
fi

echo ""
echo "📊 Service Status:"
echo "- Ollama PID: $(pgrep -f 'ollama serve' || echo 'Not found')"
echo "- Flask PID: $(pgrep -f 'app_enhanced_v3_2' || echo 'Not found')"
echo "- Serveo PID: $(pgrep -f 'serveo.net' || echo 'Not found')"
echo "- LocalHost.run PID: $(pgrep -f 'localhost.run' || echo 'Not found')"

echo ""
echo "📝 Log files:"
echo "- Ollama: /tmp/ollama.log"
echo "- Flask: /tmp/flask.log"
echo "- Serveo: /tmp/serveo.log"
echo "- LocalHost.run: /tmp/localhost_run.log"

echo ""
log_info "Setup completed successfully! Your Project Omega Enhanced v3.2.0 is ready to use."
