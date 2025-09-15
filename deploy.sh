#!/bin/bash
# Project Omega Enhanced - Deployment Script
# This script updates and restarts the enhanced chat interface

set -e

echo "🚀 Project Omega Enhanced - Deployment Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/root/project-omega-enhanced"
BACKUP_DIR="/root/backups/$(date +%Y%m%d_%H%M%S)"
SERVICE_NAME="omega-chat"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup of current installation
print_status "Creating backup of current installation..."
if [ -d "$APP_DIR" ]; then
    mkdir -p "$(dirname $BACKUP_DIR)"
    cp -r "$APP_DIR" "$BACKUP_DIR"
    print_success "Backup created at $BACKUP_DIR"
fi

# Stop existing services
print_status "Stopping existing Flask application..."
pkill -f "python.*app.py" || print_warning "No Flask app process found"

# Create application directory
print_status "Setting up application directory..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Copy new application files (assuming they're in current directory)
print_status "Copying application files..."
cp -r /workspace/project-omega-enhanced/* "$APP_DIR/"

# Install/update Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Set permissions
print_status "Setting file permissions..."
chmod +x deploy.sh
chmod 644 app.py templates/index.html requirements.txt

# Start the enhanced application
print_status "Starting Project Omega Enhanced..."
cd "$APP_DIR"

# Start in background with proper logging
nohup python3 app.py > /var/log/omega-enhanced.log 2>&1 &
APP_PID=$!

# Wait a moment and check if the service started successfully
sleep 3
if ps -p $APP_PID > /dev/null; then
    print_success "Project Omega Enhanced started successfully!"
    print_success "PID: $APP_PID"
    print_success "Log file: /var/log/omega-enhanced.log"
    print_success "Application available on port 5000"
else
    print_error "Failed to start Project Omega Enhanced"
    print_error "Check the log file for details: /var/log/omega-enhanced.log"
    exit 1
fi

# Display running services
print_status "Current running services:"
echo "Ollama API: $(pgrep ollama >/dev/null && echo 'Running' || echo 'Not running')"
echo "FastAPI: $(pgrep -f 'fastapi' >/dev/null && echo 'Running' || echo 'Not running')"
echo "Flask App: $(ps -p $APP_PID >/dev/null && echo 'Running' || echo 'Not running')"
echo "Cloudflare Tunnel: $(pgrep cloudflared >/dev/null && echo 'Running' || echo 'Not running')"

print_success "🎉 Project Omega Enhanced deployment completed!"
print_success "Access your enhanced chat interface via the Cloudflare tunnel URL"

# Show recent log entries
print_status "Recent application logs:"
tail -n 10 /var/log/omega-enhanced.log 2>/dev/null || echo "No logs available yet"
