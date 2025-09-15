#!/bin/bash

echo "=== Project Omega v3.2.0 - RunPod Port 5000 Fix ==="
echo "Ensuring reliable port 5000 access for Project Omega Enhanced"

# Kill any existing processes on port 5000
echo "Stopping any processes using port 5000..."
fuser -k 5000/tcp 2>/dev/null || true
pkill -f "app_enhanced_v3_2.py" 2>/dev/null || true

# Verify Ollama is running
echo "Checking Ollama service..."
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Starting Ollama service..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 5
    echo "Ollama service started"
else
    echo "Ollama service is already running"
fi

# Verify models are available
echo "Checking installed models..."
MODELS_COUNT=$(ollama list 2>/dev/null | wc -l)
if [ "$MODELS_COUNT" -lt 2 ]; then
    echo "Installing required models..."
    ollama pull mistral:7b-instruct &
    ollama pull llama3.2:3b-instruct &
    ollama pull phi3:mini &
    ollama pull qwen2:1.5b-instruct &
    wait
    echo "Models installation completed"
else
    echo "Models are already installed ($MODELS_COUNT available)"
fi

# Navigate to project directory
cd /workspace/Project-Omega || cd /root/Project-Omega || {
    echo "❌ Error: Project-Omega directory not found!"
    echo "Please ensure you're in the correct directory"
    exit 1
}

# Verify the app file exists and is configured correctly
if [ ! -f "app_enhanced_v3_2.py" ]; then
    echo "❌ Error: app_enhanced_v3_2.py not found!"
    echo "Current directory: $(pwd)"
    echo "Files available: $(ls -la)"
    exit 1
fi

# Check if app is configured to bind to 0.0.0.0:5000
echo "Verifying app configuration..."
if grep -q "host='0.0.0.0'" app_enhanced_v3_2.py && grep -q "port=5000" app_enhanced_v3_2.py; then
    echo "✅ App is correctly configured for port 5000 on all interfaces"
else
    echo "❌ Error: App may not be configured correctly for external access"
    echo "Checking current configuration:"
    grep -n "host=" app_enhanced_v3_2.py
    grep -n "port=" app_enhanced_v3_2.py
fi

# Start the application
echo "Starting Project Omega Enhanced v3.2.0..."
nohup python app_enhanced_v3_2.py > /tmp/app.log 2>&1 &
APP_PID=$!

# Wait a moment for startup
sleep 8

# Verify the application started successfully
if ps -p $APP_PID > /dev/null; then
    echo "✅ Application started successfully (PID: $APP_PID)"
    
    # Test local connectivity
    echo "Testing local connectivity..."
    if curl -s http://localhost:5000 > /dev/null; then
        echo "✅ Local access working: http://localhost:5000"
    else
        echo "⚠️  Local access test failed"
    fi
    
    # Display access methods
    echo ""
    echo "🚀 PROJECT OMEGA v3.2.0 IS READY!"
    echo ""
    echo "📡 Access Methods:"
    echo "1. RunPod Proxy (Recommended):"
    echo "   https://[YOUR-POD-ID]-5000.proxy.runpod.net"
    echo "   (Replace [YOUR-POD-ID] with actual pod ID from RunPod console)"
    echo ""
    echo "2. Direct Port Access:"
    echo "   - Ensure port 5000 is exposed in RunPod console"
    echo "   - Access via: http://[RUNPOD-IP]:[EXTERNAL-PORT]"
    echo ""
    echo "📊 Current Status:"
    echo "   - Application PID: $APP_PID"
    echo "   - Port 5000: $(netstat -tlnp 2>/dev/null | grep :5000 | wc -l) process(es) listening"
    echo "   - Ollama Models: $(ollama list 2>/dev/null | tail -n +2 | wc -l) installed"
    echo ""
    echo "📝 Logs:"
    echo "   - Application: tail -f /tmp/app.log"
    echo "   - Ollama: tail -f /tmp/ollama.log"
    echo ""
    
else
    echo "❌ Application failed to start!"
    echo "Check logs for details:"
    echo "tail /tmp/app.log"
    exit 1
fi

# Create a quick status check script
cat > /tmp/omega_status.sh << 'EOF'
#!/bin/bash
echo "=== Project Omega Status ==="
echo "App Process: $(ps aux | grep app_enhanced_v3_2.py | grep -v grep | wc -l)"
echo "Ollama Process: $(ps aux | grep 'ollama serve' | grep -v grep | wc -l)" 
echo "Port 5000: $(netstat -tlnp 2>/dev/null | grep :5000 | wc -l) listener(s)"
echo "Models: $(ollama list 2>/dev/null | tail -n +2 | wc -l) installed"
echo "Local Test: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5000)"
EOF
chmod +x /tmp/omega_status.sh

echo "💡 Quick status check: /tmp/omega_status.sh"
echo ""
echo "🎯 Port 5000 is now properly configured and accessible!"
