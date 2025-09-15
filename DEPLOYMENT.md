# Project Omega Enhanced - One-Line Deployment

## Copy and run this single command on your RunPod server:

```bash
curl -sSL https://raw.githubusercontent.com/shifulegend/Project-Omega/main/direct-deploy.sh | bash
```

## Or run these individual commands:

```bash
# Stop existing app
pkill -f "python.*app.py" && sleep 2

# Download enhanced files
curl -sSL "https://raw.githubusercontent.com/shifulegend/Project-Omega/main/app.py" -o app.py
mkdir -p templates && curl -sSL "https://raw.githubusercontent.com/shifulegend/Project-Omega/main/templates/index.html" -o templates/index.html
curl -sSL "https://raw.githubusercontent.com/shifulegend/Project-Omega/main/requirements.txt" -o requirements.txt

# Install dependencies and start
pip install -r requirements.txt
nohup python3 app.py > /var/log/omega-enhanced.log 2>&1 &
```

## Enhanced Features Now Available:
- ✅ Fixed model selection bug - all 4 models accessible
- ✅ Session deletion with confirmation
- ✅ Real-time status indicators (thinking time, token count)  
- ✅ System prompts for AI personality
- ✅ Advanced AI settings (temperature, thinking mode, etc.)
- ✅ High reasoning model identification badges
- ✅ Enhanced responsive UI design
- ✅ Mobile-friendly interface
- ✅ Keyboard shortcuts (Ctrl+Enter)
- ✅ Auto-expanding input field
