# 🚀 Project Omega Enhanced v3.0.0

**Advanced AI Chat Interface with Multi-Tunnel Support, Self-Learning, Internet Access & Agent Mode**

---

## 🌟 New Features in v3.0.0

### 🌐 Multiple Tunnel Providers
- **Cloudflare Tunnel** - Primary, fastest option
- **ngrok** - Alternative when Cloudflare is blocked
- **LocalTunnel** - Additional backup option
- **Serveo** - SSH-based tunneling option
- Automatic failover and multiple simultaneous URLs

### 🧠 Self-Learning AI System
- **Feedback Collection** - Rate and correct AI responses
- **Learning Database** - Persistent storage of improvements
- **Learning Application** - AI learns from past mistakes
- **Learning Logs** - Track AI improvement over time
- **Effectiveness Scoring** - Measure learning success

### 🔍 Internet Access for All Models
- **Web Search Integration** - All models can search the internet
- **Current Information** - Access to latest data and news
- **Context Enhancement** - Automatic search for relevant information
- **DuckDuckGo Integration** - Privacy-focused search

### 🖥️ Agent Mode with RunPod Access
- **Terminal Commands** - Execute shell commands via chat
- **System Administration** - Full RunPod environment access
- **Security Controls** - Safe command filtering
- **File Management** - Manage files and directories
- **Development Tools** - Install packages, run scripts

### ⚙️ Enhanced User Interface
- **Improved Settings** - More control over AI behavior
- **Real-time Status** - Connection and feature indicators
- **Tooltip Help** - Explanations for all settings
- **Mobile Responsive** - Works on all devices
- **Dark/Light Themes** - Coming soon

---

## 🚀 Quick Start

### 1. Setup (Run once)
```bash
# Make setup script executable
chmod +x setup_enhanced_v3.sh

# Run setup (installs all dependencies and tunnel providers)
./setup_enhanced_v3.sh
```

### 2. Launch Application
```bash
# Start the enhanced application
./launch_enhanced.sh
```

### 3. Manage Tunnels
```bash
# Start all tunnel providers
./manage_tunnels.sh start

# Check tunnel status
./manage_tunnels.sh status

# View tunnel logs
./manage_tunnels.sh logs

# Stop all tunnels
./manage_tunnels.sh stop
```

---

## 🎯 Usage Guide

### 💬 Basic Chat
1. Open any of the provided tunnel URLs
2. Select your preferred AI model
3. Adjust settings (temperature, tokens, etc.)
4. Start chatting!

### 🧠 Teaching the AI
1. When AI makes a mistake, click "📝 Provide Feedback"
2. Describe what was wrong and what should be correct
3. AI learns and won't repeat the mistake
4. View learning progress at `/learning_logs`

### 🌐 Internet-Enhanced Responses
1. Enable "Internet Access" in settings
2. Ask about current events, latest news, or recent information
3. AI will automatically search and include relevant web results

### 🖥️ Agent Mode Commands
1. Enable "Agent Mode" or select "RunPod Agent Mode" model
2. Use commands like:
   ```
   /cmd ls -la                    # List files
   /terminal pwd                  # Show current directory
   /cmd python --version          # Check Python version
   /cmd pip install requests      # Install packages
   /cmd cat /etc/os-release       # Check OS info
   ```

---

## 📊 Features Overview

| Feature | Description | Status |
|---------|-------------|--------|
| 🌐 Multi-Tunnel | 4 tunnel providers | ✅ Active |
| 🧠 Self-Learning | AI learns from feedback | ✅ Active |
| 🔍 Internet Access | Web search integration | ✅ Active |
| 🖥️ Agent Mode | Terminal command execution | ✅ Active |
| 💬 Chat Sessions | Multiple conversation threads | ✅ Active |
| ⚙️ AI Settings | Temperature, tokens, thinking mode | ✅ Active |
| 📱 Mobile Support | Responsive design | ✅ Active |
| 📊 Analytics | Learning logs and statistics | ✅ Active |
| 🔐 Security | Safe command filtering | ✅ Active |
| 🎨 Themes | Dark/light mode | 🚧 Coming Soon |

---

## 🔧 Configuration

### Model Settings
- **Temperature**: Controls response creativity (0.1 = focused, 1.5 = creative)
- **Max Tokens**: Maximum response length (256-4096)
- **Thinking Mode**: Shows AI reasoning process
- **Internet Access**: Enables web search capabilities
- **Agent Mode**: Allows terminal command execution

### Tunnel Providers
Edit `TUNNEL_PROVIDERS` in `app_enhanced_v3.py` to:
- Enable/disable specific providers
- Change priority order
- Add custom tunnel services

### Learning System
- Feedback is stored in `ai_learnings.db`
- Learning effectiveness is scored 0-10
- Applied learnings are tracked across sessions

---

## 📁 File Structure

```
project-omega/
├── 📄 app_enhanced_v3.py          # Main enhanced application
├── 📁 templates/
│   ├── 📄 index_enhanced_v3.html  # Enhanced web interface
│   └── 📄 learning_logs.html      # Learning logs viewer
├── 📄 setup_enhanced_v3.sh        # Setup script
├── 📄 launch_enhanced.sh          # Launch script
├── 📄 manage_tunnels.sh           # Tunnel management
├── 📄 requirements_enhanced_v3.txt # Python dependencies
├── 🗄️ chat_sessions.db            # Chat history
├── 🗄️ ai_learnings.db             # AI learning data
├── 🗄️ tunnel_providers.db         # Tunnel URL storage
└── 📁 logs/                       # Application logs
```

---

## 🌐 Tunnel Providers

### Cloudflare Tunnel
- **Pros**: Fast, reliable, no account required
- **Cons**: May be blocked by some ISPs
- **URL Format**: `https://xxx.trycloudflare.com`

### ngrok
- **Pros**: Widely compatible, stable
- **Cons**: Requires account for persistent URLs
- **URL Format**: `https://xxx.ngrok-free.app`

### LocalTunnel
- **Pros**: No account required, simple
- **Cons**: Less reliable, occasional downtime
- **URL Format**: `https://xxx.loca.lt`

### Serveo
- **Pros**: SSH-based, highly compatible
- **Cons**: Requires SSH client
- **URL Format**: `https://xxx.serveo.net`

---

## 🔒 Security

### Agent Mode Safety
- Dangerous commands are automatically blocked
- Commands have 30-second timeout limit
- Execution is sandboxed to user directory
- All commands are logged for audit

### Blocked Commands
- `rm -rf /` (system deletion)
- `shutdown`, `reboot`, `halt` (system control)
- `mkfs` (filesystem formatting)
- Fork bombs and malicious patterns

### Learning Data
- Feedback is stored locally in SQLite
- No external data transmission
- User can export/delete learning data

---

## 🆘 Troubleshooting

### Connection Issues
1. Check tunnel status: `./manage_tunnels.sh status`
2. View tunnel logs: `./manage_tunnels.sh logs`
3. Try alternative tunnel URLs
4. Restart tunnels: `./manage_tunnels.sh stop && ./manage_tunnels.sh start`

### AI Model Issues
1. Check Ollama service: `ollama serve`
2. List available models: `ollama list`
3. Pull missing models: `ollama pull mistral:7b-instruct`

### Agent Mode Issues
1. Verify RunPod environment permissions
2. Check command syntax: `/cmd [your-command]`
3. Review security restrictions in logs

### Learning System Issues
1. Check database permissions: `ls -la *.db`
2. View learning logs at `/learning_logs`
3. Reset learning database if corrupted

---

## 📈 Performance Tips

### Optimal Settings
- **CPU**: Use temperature 0.3-0.7 for balanced responses
- **Memory**: Max tokens 2048 for most use cases
- **Network**: Multiple tunnels provide redundancy

### Model Selection
- **mistral:7b-instruct**: Best for general conversation
- **codellama:13b-instruct**: Optimal for programming
- **wizardlm-uncensored:13b**: Advanced reasoning tasks
- **agent-mode**: System administration tasks

---

## 🔄 Updates

### Automatic Updates
```bash
# Pull latest changes
git pull origin main

# Run setup to install new dependencies
./setup_enhanced_v3.sh

# Restart application
./launch_enhanced.sh
```

### Manual Updates
1. Backup your databases: `cp *.db backups/`
2. Update application files
3. Run setup script: `./setup_enhanced_v3.sh`
4. Restart: `./launch_enhanced.sh`

---

## 📞 Support

### Getting Help
1. Check logs: `tail -f *.log`
2. Review troubleshooting section above
3. Visit learning logs: `/learning_logs`
4. Check tunnel status: `./manage_tunnels.sh status`

### Reporting Issues
Include the following information:
- OS and Python version
- Error messages from logs
- Steps to reproduce the issue
- Tunnel provider being used

---

## 🎯 Future Enhancements

### Planned Features
- 🎨 **Dark/Light Themes** - User interface themes
- 📱 **Mobile App** - Native mobile application
- 🔗 **API Access** - RESTful API for integration
- 🌍 **Multi-Language** - International language support
- 📊 **Advanced Analytics** - Detailed usage statistics
- 🤝 **Team Collaboration** - Multi-user support
- 🔌 **Plugin System** - Extensible functionality
- ☁️ **Cloud Sync** - Cross-device synchronization

### Contribution
We welcome contributions! Areas for improvement:
- Additional tunnel providers
- Enhanced security features
- Better learning algorithms
- User interface improvements
- Mobile optimization

---

## 📜 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- **Ollama** - Local AI model hosting
- **Flask** - Web framework
- **SocketIO** - Real-time communication
- **Cloudflare** - Tunnel services
- **ngrok** - Alternative tunneling
- **LocalTunnel** - Backup tunneling
- **Serveo** - SSH-based tunneling

---

**Project Omega Enhanced v3.0.0** - Pushing the boundaries of AI chat interfaces! 🚀