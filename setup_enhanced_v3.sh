#!/bin/bash

# Project Omega Enhanced v3.0.0 Setup Script
# Installs all tunnel providers and dependencies

echo "🚀 Setting up Project Omega Enhanced v3.0.0..."

# Update system packages
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements_enhanced_v3.txt

# Install Cloudflare tunnel (already installed)
echo "☁️ Cloudflare tunnel already available"

# Install ngrok
echo "📡 Installing ngrok..."
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | gpg --dearmor -o /etc/apt/keyrings/ngrok.gpg
echo "deb [signed-by=/etc/apt/keyrings/ngrok.gpg] https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list
apt update && apt install ngrok -y

# Install Node.js and npm for localtunnel
echo "🟢 Installing Node.js and localtunnel..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt-get install -y nodejs
npm install -g localtunnel

# Install SSH (for serveo) - usually pre-installed
echo "🔐 Ensuring SSH is available..."
apt install openssh-client -y

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p templates
mkdir -p logs
mkdir -p databases

# Set permissions
echo "🔒 Setting permissions..."
chmod +x app_enhanced_v3.py
chmod 644 templates/*.html
chmod 666 *.db 2>/dev/null || true

# Create launch script
echo "📝 Creating launch script..."
cat > launch_enhanced.sh << 'EOF'
#!/bin/bash

echo "🚀 Launching Project Omega Enhanced v3.0.0..."

# Kill any existing processes
pkill -f "app_enhanced_v3.py"
pkill -f "cloudflared"
pkill -f "ngrok"
pkill -f "lt"

# Wait a moment
sleep 2

# Start the enhanced application
cd "$(dirname "$0")"
python3 app_enhanced_v3.py

EOF

chmod +x launch_enhanced.sh

# Create tunnel management script
cat > manage_tunnels.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        echo "🌐 Starting all tunnel providers..."
        nohup cloudflared tunnel --url http://localhost:5000 > tunnel_cloudflare.log 2>&1 &
        nohup ngrok http 5000 > tunnel_ngrok.log 2>&1 &
        nohup lt --port 5000 > tunnel_localtunnel.log 2>&1 &
        echo "Tunnels started. Check logs for URLs."
        ;;
    stop)
        echo "🛑 Stopping all tunnels..."
        pkill -f "cloudflared"
        pkill -f "ngrok"
        pkill -f "lt"
        pkill -f "serveo"
        echo "All tunnels stopped."
        ;;
    status)
        echo "📊 Tunnel status:"
        pgrep -f "cloudflared" > /dev/null && echo "✅ Cloudflare: Running" || echo "❌ Cloudflare: Stopped"
        pgrep -f "ngrok" > /dev/null && echo "✅ ngrok: Running" || echo "❌ ngrok: Stopped"
        pgrep -f "lt" > /dev/null && echo "✅ LocalTunnel: Running" || echo "❌ LocalTunnel: Stopped"
        pgrep -f "serveo" > /dev/null && echo "✅ Serveo: Running" || echo "❌ Serveo: Stopped"
        ;;
    logs)
        echo "📋 Recent tunnel logs:"
        echo "=== Cloudflare ==="
        tail -n 10 tunnel_cloudflare.log 2>/dev/null || echo "No Cloudflare logs"
        echo "=== ngrok ==="
        tail -n 10 tunnel_ngrok.log 2>/dev/null || echo "No ngrok logs"
        echo "=== LocalTunnel ==="
        tail -n 10 tunnel_localtunnel.log 2>/dev/null || echo "No LocalTunnel logs"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|logs}"
        exit 1
        ;;
esac

EOF

chmod +x manage_tunnels.sh

# Create systemd service for auto-start (optional)
cat > project-omega-enhanced.service << 'EOF'
[Unit]
Description=Project Omega Enhanced v3.0.0
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/project-omega
ExecStart=/usr/bin/python3 app_enhanced_v3.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "
🎉 Project Omega Enhanced v3.0.0 Setup Complete!

📚 Quick Start:
   ./launch_enhanced.sh           # Start the enhanced application
   ./manage_tunnels.sh start      # Start all tunnel providers
   ./manage_tunnels.sh status     # Check tunnel status
   ./manage_tunnels.sh logs       # View tunnel logs

🌟 New Features:
   • 🌐 Multiple tunnel providers (Cloudflare, ngrok, LocalTunnel, Serveo)
   • 🧠 Self-learning AI with feedback system
   • 🔍 Internet access for all models
   • 🖥️ Agent mode with RunPod terminal access
   • ⚙️ Enhanced AI settings with tooltips

🔗 Access URLs:
   The application will start multiple tunnels automatically.
   Check the web interface for all available URLs.

📊 Learning Logs:
   Visit /learning_logs to view AI learning progress.

🤖 Agent Mode:
   Use '/cmd [command]' in chat for terminal access.

Happy chatting! 🚀
"