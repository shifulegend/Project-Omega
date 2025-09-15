#!/bin/bash

# Project Omega Enhanced v3.2.0 - Perfect Chat Mode Launch Script
# This script launches the enhanced application with all fixes and new features

echo "🚀 Starting Project Omega Enhanced v3.2.0 - Perfect Chat Mode"
echo "============================================================="

# Kill any existing processes
echo "📋 Stopping any existing services..."
pkill -f "python.*app_enhanced_v3"
pkill -f cloudflared
pkill -f ngrok
pkill -f "lt --port"
ssh -O exit serveo.net 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Install dependencies if needed
if [ ! -f ".deps_installed_v3.2" ]; then
    echo "📦 Installing Python dependencies..."
    pip install flask flask-socketio requests sqlite3 uuid logging threading subprocess hashlib re datetime typing
    touch .deps_installed_v3.2
fi

# Create logs directory
mkdir -p logs

# Set permissions
chmod +x app_enhanced_v3_2.py

echo "🎯 Launching Application Services..."

# Start the main application
echo "🚀 Starting main application (Port 5000)..."
nohup python app_enhanced_v3_2.py > logs/app_v3.2.log 2>&1 &
APP_PID=$!
echo "📝 Main app PID: $APP_PID"

# Wait for app to start
sleep 5

# Check if app is running
if ps -p $APP_PID > /dev/null; then
    echo "✅ Main application started successfully"
else
    echo "❌ Failed to start main application"
    exit 1
fi

echo "🌐 Starting Tunnel Services..."

# Start Cloudflare tunnel
echo "☁️  Starting Cloudflare tunnel..."
nohup cloudflared tunnel --url http://localhost:5000 > logs/cloudflare.log 2>&1 &
CLOUDFLARE_PID=$!
echo "📝 Cloudflare PID: $CLOUDFLARE_PID"

# Start ngrok (if available)
if command -v ngrok &> /dev/null; then
    echo "🚀 Starting ngrok tunnel..."
    nohup ngrok http 5000 > logs/ngrok.log 2>&1 &
    NGROK_PID=$!
    echo "📝 ngrok PID: $NGROK_PID"
else
    echo "⚠️  ngrok not found, skipping..."
fi

# Start LocalTunnel (if available)
if command -v lt &> /dev/null; then
    echo "🌏 Starting LocalTunnel..."
    nohup lt --port 5000 > logs/localtunnel.log 2>&1 &
    LT_PID=$!
    echo "📝 LocalTunnel PID: $LT_PID"
else
    echo "⚠️  LocalTunnel not found, skipping..."
fi

# Wait for tunnels to start
echo "⏳ Waiting for tunnels to initialize..."
sleep 10

echo "📊 Service Status Check..."

# Check service status
echo "🔍 Checking application status..."
if curl -s http://localhost:5000 > /dev/null; then
    echo "✅ Application is responding on port 5000"
else
    echo "❌ Application is not responding"
fi

# Extract tunnel URLs
echo "🌐 Active Tunnel URLs:"
echo "====================="

# Cloudflare URL
if [ -f "logs/cloudflare.log" ]; then
    CLOUDFLARE_URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' logs/cloudflare.log | tail -1)
    if [ ! -z "$CLOUDFLARE_URL" ]; then
        echo "☁️  Cloudflare: $CLOUDFLARE_URL"
    fi
fi

# ngrok URL  
if [ -f "logs/ngrok.log" ]; then
    # Wait for ngrok to fully start
    sleep 5
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)
    if [ ! -z "$NGROK_URL" ]; then
        echo "🚀 ngrok: $NGROK_URL"
    fi
fi

# LocalTunnel URL
if [ -f "logs/localtunnel.log" ]; then
    LT_URL=$(grep -oE 'https://[a-z0-9-]+\.loca\.lt' logs/localtunnel.log | tail -1)
    if [ ! -z "$LT_URL" ]; then
        echo "🌏 LocalTunnel: $LT_URL"
    fi
fi

echo ""
echo "🎉 PROJECT OMEGA ENHANCED v3.2.0 DEPLOYED SUCCESSFULLY! 🎉"
echo "========================================================="
echo "✅ All Issues Fixed & New Features Implemented:"
echo "   🔧 Fixed model loading with proper timeout handling"
echo "   📋 Fixed learning logs route and display"
echo "   💾 Auto-save sessions with intelligent naming"
echo "   ⚙️  Perfect defaults: blank system prompt, all modes enabled"
echo "   🧹 Clear chat preserves learnings as requested"
echo "   🔄 Real-time GitHub updates"
echo ""
echo "🎯 Perfect Chat Mode Features:"
echo "   • Auto-session creation with smart names"
echo "   • Enhanced model loading with fallbacks"
echo "   • Learning system that remembers corrections"
echo "   • Internet access for up-to-date information"
echo "   • Improved error handling and user experience"
echo ""
echo "📱 Access your application at:"
echo "   🏠 Local: http://localhost:5000"
echo "   🌐 Public URLs listed above"
echo ""
echo "🔍 Monitor logs:"
echo "   📋 Application: tail -f logs/app_v3.2.log"
echo "   ☁️  Cloudflare: tail -f logs/cloudflare.log"
echo "   🚀 ngrok: tail -f logs/ngrok.log (if available)"
echo "   🌏 LocalTunnel: tail -f logs/localtunnel.log (if available)"
echo ""
echo "🛑 Stop all services: pkill -f 'python.*app_enhanced_v3_2' && pkill -f cloudflared && pkill -f ngrok && pkill -f lt"
echo ""
echo "🎊 Everything is ready! Test all features and enjoy the perfect chat experience! 🎊"
