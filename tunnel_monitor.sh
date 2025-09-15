#!/bin/bash

# Project Omega Enhanced v3.2.0 - Tunnel Monitor Script
# Ensures continuous public access via tunnels

echo "🌐 Project Omega v3.2.0 - Tunnel Monitor"
echo "========================================"

while true; do
    # Check if Serveo tunnel is running
    if ! pgrep -f "serveo.net" > /dev/null; then
        echo "🔄 Restarting Serveo tunnel..."
        nohup ssh -o "StrictHostKeyChecking=no" -R 80:localhost:5000 serveo.net > /tmp/serveo.log 2>&1 &
        sleep 5
        
        # Extract URL from logs
        if [ -f /tmp/serveo.log ]; then
            SERVEO_URL=$(grep -o 'https://[^[:space:]]*\.serveo\.net' /tmp/serveo.log | tail -1)
            if [ ! -z "$SERVEO_URL" ]; then
                echo "✅ Serveo tunnel active: $SERVEO_URL"
                echo "$SERVEO_URL" > /tmp/current_tunnel_url.txt
            fi
        fi
    fi
    
    # Test if application is responding
    if curl -s http://localhost:5000 | grep -q "Project Omega"; then
        echo "✅ Application is running on localhost:5000"
    else
        echo "❌ Application not responding on localhost:5000"
    fi
    
    # Display current tunnel URL
    if [ -f /tmp/current_tunnel_url.txt ]; then
        CURRENT_URL=$(cat /tmp/current_tunnel_url.txt)
        echo "🌐 Current Public URL: $CURRENT_URL"
    fi
    
    sleep 30
done