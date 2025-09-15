#!/bin/bash
# Project Omega Enhanced - Direct Deployment Commands
# Copy and paste these commands directly on your RunPod server

echo "🚀 Project Omega Enhanced Deployment"

# Stop existing Flask app
pkill -f "python.*app.py" || echo "No Flask app found"
sleep 2

# Download the enhanced app.py
curl -sSL "https://raw.githubusercontent.com/shifulegend/Project-Omega/main/app.py" -o app.py

# Create templates directory and download enhanced HTML
mkdir -p templates
curl -sSL "https://raw.githubusercontent.com/shifulegend/Project-Omega/main/templates/index.html" -o templates/index.html

# Download requirements and install
curl -sSL "https://raw.githubusercontent.com/shifulegend/Project-Omega/main/requirements.txt" -o requirements.txt
pip install -r requirements.txt

# Initialize enhanced database
python3 -c "
import sqlite3
DATABASE_PATH = 'chat_sessions.db'
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_name TEXT NOT NULL,
        model_name TEXT NOT NULL,
        system_prompt TEXT DEFAULT '',
        temperature REAL DEFAULT 0.7,
        thinking_mode TEXT DEFAULT 'auto',
        thinking_budget INTEGER DEFAULT 10000,
        max_tokens INTEGER DEFAULT 2048,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        thinking_time REAL DEFAULT 0,
        token_count INTEGER DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
    )
''')
conn.commit()
conn.close()
print('✅ Database schema updated')
"

# Start the enhanced application
echo "🚀 Starting Project Omega Enhanced..."
nohup python3 app.py > /var/log/omega-enhanced.log 2>&1 &

sleep 3
echo "✅ Project Omega Enhanced deployed!"
echo "📊 Check status: tail -f /var/log/omega-enhanced.log"
echo "🌐 Access via your Cloudflare tunnel URL"
echo ""
echo "🎉 New Features Active:"
echo "  ✅ Fixed model selection - all 4 models working"
echo "  ✅ Session deletion (hover ❌ on sessions)"
echo "  ✅ Real-time status with thinking time & token count"
echo "  ✅ System prompts for AI personality"
echo "  ✅ Advanced AI settings (temperature, thinking mode)"
echo "  ✅ High reasoning model badges"
echo "  ✅ Enhanced responsive UI"
