#!/bin/bash

# Project Omega Enhanced v3.1.0 Launch Script
echo "🚀 Launching Project Omega Enhanced v3.1.0..."

# Kill any existing processes
echo "🛑 Stopping existing services..."
pkill -f "app_enhanced_v3_1.py" 2>/dev/null
pkill -f "app_enhanced_v3.py" 2>/dev/null
pkill -f "app.py" 2>/dev/null
pkill -f "cloudflared" 2>/dev/null
pkill -f "ngrok" 2>/dev/null
pkill -f "lt" 2>/dev/null

# Wait for processes to stop
sleep 3

# Start the enhanced application
echo "🌟 Starting Project Omega Enhanced v3.1.0..."
cd "$(dirname "$0")"

# Install/update dependencies
pip3 install flask flask-socketio requests > /dev/null 2>&1

# Start the application in background
nohup python3 app_enhanced_v3_1.py > omega_v3_1.log 2>&1 &
APP_PID=$!

echo "✅ Application started with PID: $APP_PID"

# Wait for application to start
echo "⏳ Waiting for application to initialize..."
sleep 5

# Check if application is running
if ps -p $APP_PID > /dev/null; then
    echo "✅ Application is running successfully!"
    echo "📊 Checking logs..."
    sleep 2
    
    # Show recent logs
    echo "📋 Recent activity:"
    tail -n 15 omega_v3_1.log | grep -E "(INFO|Tunnel.*active|Running on)"
    
    echo ""
    echo "🎉 Project Omega Enhanced v3.1.0 is LIVE!"
    echo ""
    echo "🔗 Access Methods:"
    echo "   • Check application logs for tunnel URLs"
    echo "   • Look for 'Tunnel.*active at:' messages"
    echo ""
    echo "🌟 New Features:"
    echo "   ✅ Fixed 404 errors - separate agent sessions"
    echo "   ✅ Dynamic model detection from Ollama API"  
    echo "   ✅ Natural language agent mode"
    echo "   ✅ Tunnel URLs hidden in settings panel"
    echo "   ✅ Improved session management"
    echo ""
    echo "💡 Usage:"
    echo "   • 💬 Chat Mode: Regular AI conversation"
    echo "   • 🖥️ Agent Mode: Natural language commands"
    echo "   • ⚙️ Settings: Access tunnel URLs and configuration"
    echo ""
    echo "📝 Monitor logs: tail -f omega_v3_1.log"
    echo "🛑 Stop application: pkill -f app_enhanced_v3_1.py"
    
else
    echo "❌ Failed to start application. Check logs:"
    tail -n 20 omega_v3_1.log
    exit 1
fi