# Project Omega Enhanced v3.2.0 🧠

Advanced AI Chat Interface with Session Management, Perfect Chat Mode, and Real-time AI Model Integration

![Project Omega Enhanced](https://img.shields.io/badge/Status-v3.2.0-brightgreen) ![Flask](https://img.shields.io/badge/Flask-Latest-blue) ![SocketIO](https://img.shields.io/badge/SocketIO-Latest-orange) ![RunPod](https://img.shields.io/badge/RunPod-Ready-purple)

## 🚀 Features

### ✅ **Current Models (v3.2.0)**
- **Mistral 7B Instruct** (4.1GB) - Fast and efficient general-purpose model
- **Llama 3.2 3B Instruct** (2.0GB) - Advanced reasoning with thinking mode support
- **Phi-3 Mini** (2.3GB) - Compact high-performance model with thinking support  
- **Qwen2 1.5B Instruct** (1.0GB) - Ultra-fast lightweight model

### ✅ **Perfect Chat Mode Implementation**
- **Fixed Model Loading**: Proper timeout handling and error recovery
- **Auto-save Sessions**: Intelligent session naming with timestamp tracking
- **Default Settings**: Blank system prompt, all modes enabled by default

### 🆕 **New Features**

#### **Session Management**
- ✅ **Create unlimited chat sessions** with custom names
- ✅ **Delete sessions** with confirmation dialog
- ✅ **Session persistence** with SQLite database
- ✅ **Automatic session updates** with timestamp tracking

#### **Advanced AI Settings**
- ✅ **System Prompts**: Set custom personality/behavior for each session
- ✅ **Temperature Control**: Fine-tune response creativity (0.0-2.0)
- ✅ **Token Limits**: Configure maximum response length
- ✅ **Thinking Mode**: Enable advanced reasoning for supported models
- ✅ **Thinking Budget**: Control reasoning depth (tokens allocated for thinking)

#### **Real-time Status & Analytics**
- ✅ **Live Status Indicators**: "Ready", "Thinking...", "Error" states
- ✅ **Thinking Time Display**: See how long the AI spent processing
- ✅ **Token Usage Tracking**: Monitor token consumption per message
- ✅ **Model Identification**: Clear labels for "High Reasoning" vs "Standard" models

#### **Enhanced User Experience**
- ✅ **Responsive Design**: Works on desktop, tablet, and mobile
- ✅ **Keyboard Shortcuts**: Ctrl+Enter to send messages
- ✅ **Auto-expanding Input**: Text area grows with content
- ✅ **Message Timestamps**: Track conversation flow
- ✅ **Visual Model Badges**: Instant recognition of model capabilities

## 🏗️ Architecture

### **Backend (Flask + SocketIO)**
- **Real-time Communication**: WebSocket-based chat with instant updates
- **Database Layer**: SQLite for persistent session and message storage
- **API Integration**: Direct connection to Ollama and FastAPI services
- **Configuration Management**: Model-specific settings and capabilities

### **Frontend (Vanilla JavaScript + CSS)**
- **Modern UI**: Gradient backgrounds, blur effects, smooth animations
- **Modal System**: Intuitive settings and session management
- **Real-time Updates**: Live status indicators and message streaming
- **Responsive Layout**: Sidebar + main chat area with mobile optimization

### **Model Configuration**
```json
{
  "mistral:7b-instruct": {
    "name": "Mistral 7B Instruct",
    "type": "standard",
    "supports_thinking": false,
    "default_temperature": 0.7,
    "description": "Fast and efficient general-purpose model"
  },
  "wizardlm-uncensored:13b": {
    "name": "WizardLM Uncensored 13B", 
    "type": "high_reasoning",
    "supports_thinking": true,
    "default_temperature": 0.8,
    "description": "Advanced reasoning and problem-solving capabilities"
  }
}
```

## 🚀 Installation & Deployment

### **Current Version**: v3.2.0 - Perfect Chat Mode Implementation

### **Prerequisites**
- Python 3.8+
- Ollama running on port 11434 with models installed
- Port 5000 available for web interface

### **RunPod Deployment (Recommended)**

#### **Step 1: Clone Repository**
```bash
git clone https://github.com/MiniMaxAI/Project-Omega.git
cd Project-Omega
```

#### **Step 2: Run Complete Setup**
```bash
chmod +x complete_setup.sh
./complete_setup.sh
```

The setup script will:
- ✅ Start Ollama service
- ✅ Install all 4 required models (Mistral, Llama 3.2, Phi-3, Qwen2)
- ✅ Install Python dependencies
- ✅ Start the v3.2.0 application on port 5000

#### **Step 3: Access Your Application**

**Method 1: RunPod Proxy URL (Recommended)**
```
https://[YOUR-POD-ID]-5000.proxy.runpod.net
```
Replace `[YOUR-POD-ID]` with your actual pod ID from RunPod console.

**Method 2: Direct Port Access**
1. In RunPod console → Connect tab → Expose port 5000
2. Access via: `http://[YOUR-RUNPOD-IP]:[EXTERNAL-PORT]`

### **Manual Installation**

1. **Install Dependencies**
   ```bash
   pip install -r requirements_v3_2.txt
   ```

2. **Start Ollama & Install Models**
   ```bash
   nohup ollama serve > /tmp/ollama.log 2>&1 &
   ollama pull mistral:7b-instruct
   ollama pull llama3.2:3b-instruct
   ollama pull phi3:mini
   ollama pull qwen2:1.5b-instruct
   ```

3. **Run the Application**
   ```bash
   python app_enhanced_v3_2.py
   ```

4. **Access the Interface**
   - Local: `http://localhost:5000`
   - Production: Configure port forwarding for port 5000

### **Production Deployment**

Use the included deployment script for seamless updates:

```bash
chmod +x deploy.sh
./deploy.sh
```

The script will:
- ✅ Create backups of existing installation
- ✅ Stop current services gracefully
- ✅ Install/update dependencies
- ✅ Start the enhanced application
- ✅ Verify service health
- ✅ Display status of all components

## 📱 Usage Guide

### **Creating a New Session**
1. Click **"+ New Chat Session"**
2. Choose your **AI model** (see badges for capabilities)
3. Set **optional system prompt** for AI personality
4. Configure **advanced settings** (temperature, tokens, thinking mode)
5. Click **"Create Session"**

### **Managing Sessions**
- **Switch Sessions**: Click any session in the sidebar
- **Delete Sessions**: Hover over session → click ❌ button
- **Edit Settings**: Select session → click ⚙️ Settings button

### **Advanced Features**
- **System Prompts**: Define AI behavior per session
- **High Reasoning Models**: Use WizardLM or Dolphin for complex problems
- **Thinking Mode**: Enable for deeper analysis (high reasoning models only)
- **Real-time Status**: Monitor AI processing with live indicators

## 🔧 Configuration

### **Configuration**
```bash
# Application Configuration
OLLAMA_API_URL=http://localhost:11434
PORT=5000
HOST=0.0.0.0

# Database Paths
DATABASE_PATH=chat_sessions.db
LEARNINGS_DATABASE_PATH=ai_learnings.db
TUNNELS_DATABASE_PATH=tunnel_providers.db

# Model Configuration
MODEL_FETCH_TIMEOUT=5
```

### **Required Models (Auto-installed by complete_setup.sh)**
```bash
ollama pull mistral:7b-instruct      # 4.1GB - General purpose
ollama pull llama3.2:3b-instruct     # 2.0GB - Advanced reasoning  
ollama pull phi3:mini                # 2.3GB - High performance
ollama pull qwen2:1.5b-instruct      # 1.0GB - Ultra-fast
```

### **Model Types**
- **Standard Models**: Fast, efficient, good for general tasks
- **High Reasoning Models**: Advanced problem-solving, supports thinking mode

## 🛠️ Development

### **Project Structure**
```
Project-Omega/
├── app_enhanced_v3_2.py     # Main Flask application (v3.2.0)
├── complete_setup.sh        # Automated setup script for RunPod
├── test_suite.py           # Automated testing suite
├── requirements_v3_2.txt   # Python dependencies (v3.2.0)
├── templates/
│   └── index.html          # Enhanced frontend interface
├── chat_sessions.db        # SQLite database (auto-created)
├── ai_learnings.db         # AI learning storage
└── tunnel_providers.db     # Tunnel configuration storage
```

### **Key Components**
- **Session Management**: SQLite-based persistence with auto-naming
- **Real-time Communication**: Flask-SocketIO WebSockets
- **Model Configuration**: Dynamic model loading with fallback support
- **Status Tracking**: Live indicators with thinking time metrics
- **Perfect Chat Mode**: Enhanced UX with intelligent defaults

## 🐛 Troubleshooting

### **Port 5000 Access Issues**
If you can't access the application via exposed port 5000:

1. **Check if app is running on correct port:**
   ```bash
   ps aux | grep app_enhanced_v3_2
   netstat -tlnp | grep :5000
   ```

2. **Verify app binds to 0.0.0.0:5000 (not localhost):**
   ```bash
   grep -n "host=" app_enhanced_v3_2.py
   # Should show: host='0.0.0.0', port=5000
   ```

3. **Use RunPod Proxy URL (most reliable):**
   ```
   https://[YOUR-POD-ID]-5000.proxy.runpod.net
   ```

4. **Restart application properly:**
   ```bash
   pkill -f app_enhanced_v3_2
   python app_enhanced_v3_2.py
   ```

### **Model Loading Issues**
**"Cannot connect to AI model" error:**
- ✅ Check Ollama service: `ps aux | grep ollama`
- ✅ Start if needed: `nohup ollama serve > /tmp/ollama.log 2>&1 &`
- ✅ Verify models installed: `ollama list`
- ✅ Install missing models: `ollama pull mistral:7b-instruct`

**"Loading models..." stuck:**
- ✅ Check Ollama API: `curl http://localhost:11434/api/tags`
- ✅ Restart both services: `pkill -f ollama && pkill -f app_enhanced`
- ✅ Wait 10 seconds, then run `./complete_setup.sh`

### **RunPod Specific Issues**
**SSH Connection Refused:**
- Instance may have restarted - check RunPod console
- Use Web Terminal as alternative
- Verify pod is still running

**Models Not Persisting:**
- Models are stored in `/root/.ollama/`
- Use persistent storage or re-run `./complete_setup.sh`

### **General Debugging**
```bash
# Check all running processes
ps aux | grep -E "(ollama|app_enhanced|python)"

# View application logs
tail -f /tmp/app.log

# View Ollama logs  
tail -f /tmp/ollama.log

# Test model availability
curl http://localhost:11434/api/tags

# Test app health
curl http://localhost:5000
```

## 📊 Performance Metrics

### **Response Times**
- **Standard Models**: ~2-5 seconds
- **High Reasoning**: ~5-15 seconds (thinking time included)

### **Resource Usage**
- **Memory**: ~100-200MB per active session
- **Storage**: ~1KB per message (SQLite)
- **Network**: WebSocket for real-time, minimal overhead

## 🔄 Updates & Versioning

### **Current Version**: v3.2.0 - Perfect Chat Mode Implementation
- ✅ Fixed model loading with proper timeout and error handling
- ✅ Autosave sessions with auto-generated names
- ✅ Default settings: blank system prompt, all modes enabled
- ✅ Fixed learning logs route
- ✅ Clear chat preserves learnings
- ✅ Improved reliability and user experience
- ✅ Enhanced RunPod deployment support
- ✅ Port 5000 standardization

### **Upcoming Features**
- 🔄 Message search and filtering
- 🔄 Session export/import
- 🔄 Multi-user support
- 🔄 Voice input/output
- 🔄 File upload capabilities

## 📝 License

This project is part of Project Omega initiative. All rights reserved.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📞 Support

For issues, feature requests, or questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review application logs: `/var/log/omega-enhanced.log`

---

**Made with ❤️ by MiniMax Agent for Project Omega Enhanced**

*Experience the future of AI conversation with advanced session management, real-time status tracking, and intelligent model selection.*