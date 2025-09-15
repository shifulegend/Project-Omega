#!/usr/bin/env python3
"""
Project Omega Enhanced v3.1.0 - Advanced AI Chat Interface
Fixed Issues:
- Separate agent mode sessions (no 404 errors)
- Dynamic model detection from Ollama API
- Natural language command interpretation in agent mode
- Hidden tunnel management in settings panel
- Improved session management
"""

import os
import json
import sqlite3
import requests
import time
import subprocess
import threading
import hashlib
import logging
import re
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omega-enhanced-v3.1-secret-key-2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration
OLLAMA_API_URL = "http://localhost:11434"
FASTAPI_URL = "http://localhost:8000"
DATABASE_PATH = "chat_sessions.db"
LEARNINGS_DATABASE_PATH = "ai_learnings.db"
TUNNELS_DATABASE_PATH = "tunnel_providers.db"

# Active tunnels storage
ACTIVE_TUNNELS = {}
TUNNEL_PROCESSES = {}

# Tunnel provider configurations
TUNNEL_PROVIDERS = {
    "cloudflare": {
        "name": "Cloudflare Tunnel",
        "command": ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
        "url_pattern": r"https://[\w-]+\.trycloudflare\.com",
        "priority": 1,
        "enabled": True
    },
    "ngrok": {
        "name": "ngrok", 
        "command": ["ngrok", "http", "5000"],
        "url_pattern": r"https://[\w-]+\.ngrok-free\.app",
        "priority": 2,
        "enabled": True
    },
    "localtunnel": {
        "name": "LocalTunnel",
        "command": ["lt", "--port", "5000"],
        "url_pattern": r"https://[\w-]+\.loca\.lt",
        "priority": 3,
        "enabled": True
    },
    "serveo": {
        "name": "Serveo",
        "command": ["ssh", "-R", "80:localhost:5000", "serveo.net"],
        "url_pattern": r"https://[\w-]+\.serveo\.net", 
        "priority": 4,
        "enabled": True
    }
}

# Command interpretation patterns for natural language agent mode
COMMAND_PATTERNS = [
    {
        "patterns": [r"what.*python.*version", r"python.*version", r"check python"],
        "command": "python --version",
        "description": "Check Python version"
    },
    {
        "patterns": [r"list.*files", r"show.*files", r"what.*files", r"ls"],
        "command": "ls -la",
        "description": "List files in current directory"
    },
    {
        "patterns": [r"current.*directory", r"where.*am.*i", r"pwd", r"what.*directory"],
        "command": "pwd",
        "description": "Show current directory"
    },
    {
        "patterns": [r"disk.*space", r"storage.*space", r"df", r"disk.*usage"],
        "command": "df -h",
        "description": "Show disk space usage"
    },
    {
        "patterns": [r"memory.*usage", r"ram.*usage", r"free.*memory"],
        "command": "free -h",
        "description": "Show memory usage"
    },
    {
        "patterns": [r"running.*processes", r"process.*list", r"ps"],
        "command": "ps aux | head -20",
        "description": "Show running processes"
    },
    {
        "patterns": [r"system.*info", r"os.*info", r"uname"],
        "command": "uname -a",
        "description": "Show system information"
    },
    {
        "patterns": [r"ip.*address", r"network.*info", r"ifconfig"],
        "command": "ip addr show",
        "description": "Show network interfaces"
    },
    {
        "patterns": [r"install.*pip.*(.+)", r"pip.*install.*(.+)"],
        "command": "pip install {1}",
        "description": "Install Python package via pip"
    },
    {
        "patterns": [r"create.*directory.*(.+)", r"mkdir.*(.+)"],
        "command": "mkdir -p {1}",
        "description": "Create directory"
    },
    {
        "patterns": [r"remove.*file.*(.+)", r"delete.*file.*(.+)", r"rm.*(.+)"],
        "command": "rm -f {1}",
        "description": "Remove file"
    }
]

class OllamaModelManager:
    """Dynamic model detection and management"""
    
    @staticmethod
    def get_available_models() -> List[Dict]:
        """Get available models from Ollama API"""
        try:
            response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = []
                
                for model in data.get('models', []):
                    model_name = model.get('name', '')
                    model_size = model.get('size', 0)
                    
                    # Determine model capabilities based on name
                    supports_thinking = any(keyword in model_name.lower() for keyword in ['wizard', 'uncensored', 'dolphin'])
                    
                    models.append({
                        'id': model_name,
                        'name': model_name.replace(':', ' ').title(),
                        'type': 'advanced' if supports_thinking else 'standard',
                        'supports_thinking': supports_thinking,
                        'supports_internet': True,  # All models support internet
                        'size_gb': round(model_size / (1024**3), 1) if model_size else 0,
                        'description': f'Dynamic model - {round(model_size / (1024**3), 1)}GB' if model_size else 'Dynamic model'
                    })
                
                return models
            else:
                logger.error(f"Failed to fetch models: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return []
    
    @staticmethod
    def get_fallback_models() -> List[Dict]:
        """Fallback models if Ollama API is not available"""
        return [
            {
                'id': 'mistral:7b-instruct',
                'name': 'Mistral 7B Instruct',
                'type': 'standard',
                'supports_thinking': False,
                'supports_internet': True,
                'size_gb': 4.1,
                'description': 'Fast and efficient general-purpose model'
            },
            {
                'id': 'codellama:13b-instruct', 
                'name': 'CodeLlama 13B Instruct',
                'type': 'standard',
                'supports_thinking': False,
                'supports_internet': True,
                'size_gb': 7.3,
                'description': 'Specialized for code generation'
            }
        ]

class DatabaseManager:
    """Enhanced database manager"""
    
    @staticmethod
    def init_databases():
        """Initialize all databases"""
        DatabaseManager.init_sessions_db()
        DatabaseManager.init_learnings_db()
        DatabaseManager.init_tunnels_db()
    
    @staticmethod
    def init_sessions_db():
        """Initialize chat sessions database with session types"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                session_type TEXT DEFAULT 'chat',
                model TEXT NOT NULL,
                system_prompt TEXT,
                temperature REAL DEFAULT 0.7,
                max_tokens INTEGER DEFAULT 2048,
                thinking_mode BOOLEAN DEFAULT 0,
                internet_access BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()
    
    @staticmethod
    def init_learnings_db():
        """Initialize AI learnings database"""
        conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_correction TEXT NOT NULL,
                ai_mistake TEXT NOT NULL,
                context TEXT,
                model_used TEXT,
                learning_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_count INTEGER DEFAULT 0,
                effectiveness_score REAL DEFAULT 0.0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                learning_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1,
                FOREIGN KEY (learning_id) REFERENCES learnings (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()
    
    @staticmethod
    def init_tunnels_db():
        """Initialize tunnel providers database"""
        conn = sqlite3.connect(TUNNELS_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tunnel_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

class WebSearchManager:
    """Handle web search for internet-enabled models"""
    
    @staticmethod
    def search_web(query: str, max_results: int = 3) -> List[Dict]:
        """Search web using DuckDuckGo API"""
        try:
            search_url = f"https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if 'RelatedTopics' in data:
                    for topic in data['RelatedTopics'][:max_results]:
                        if isinstance(topic, dict) and 'Text' in topic:
                            results.append({
                                'title': topic.get('Text', '')[:100],
                                'url': topic.get('FirstURL', ''),
                                'snippet': topic.get('Text', '')[:200]
                            })
                
                return results
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
        
        return []
    
    @staticmethod
    def enhance_prompt_with_search(prompt: str, enable_search: bool = True) -> str:
        """Enhance user prompt with web search results if needed"""
        if not enable_search:
            return prompt
        
        search_triggers = ['latest', 'current', 'recent', 'today', 'news', 'what is', 'tell me about']
        
        if any(trigger in prompt.lower() for trigger in search_triggers):
            search_query = prompt[:100]
            search_results = WebSearchManager.search_web(search_query)
            
            if search_results:
                search_context = "\n\n[INTERNET SEARCH RESULTS]:\n"
                for i, result in enumerate(search_results, 1):
                    search_context += f"{i}. {result['title']}\n   {result['snippet']}...\n"
                
                return prompt + search_context
        
        return prompt

class LearningManager:
    """Manage AI learning and feedback system"""
    
    @staticmethod
    def record_learning(session_id: str, user_correction: str, ai_mistake: str, 
                       context: str, model_used: str) -> int:
        """Record a new learning from user feedback"""
        conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
        cursor = conn.cursor()
        
        learning_summary = f"Avoid: {ai_mistake[:50]}... | Correct: {user_correction[:50]}..."
        
        cursor.execute('''
            INSERT INTO learnings 
            (session_id, user_correction, ai_mistake, context, model_used, learning_summary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, user_correction, ai_mistake, context, model_used, learning_summary))
        
        learning_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Recorded learning {learning_id} for session {session_id}")
        return learning_id
    
    @staticmethod
    def get_relevant_learnings(prompt: str, model: str) -> List[Dict]:
        """Get relevant past learnings for current prompt"""
        conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT learning_summary, applied_count, effectiveness_score 
            FROM learnings 
            WHERE model_used = ? 
            ORDER BY effectiveness_score DESC, created_at DESC 
            LIMIT 3
        ''', (model,))
        
        learnings = cursor.fetchall()
        conn.close()
        
        return [
            {
                'summary': learning[0],
                'applied_count': learning[1],
                'effectiveness_score': learning[2]
            }
            for learning in learnings
        ]
    
    @staticmethod
    def get_learning_logs(limit: int = 50) -> List[Dict]:
        """Get recent learning logs for display"""
        conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_id, user_correction, ai_mistake, learning_summary, 
                   model_used, applied_count, effectiveness_score, created_at
            FROM learnings 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': log[0],
                'session_id': log[1],
                'user_correction': log[2],
                'ai_mistake': log[3],
                'learning_summary': log[4],
                'model_used': log[5],
                'applied_count': log[6],
                'effectiveness_score': log[7],
                'created_at': log[8]
            }
            for log in logs
        ]

class TunnelManager:
    """Manage multiple tunnel providers"""
    
    @staticmethod
    def start_all_tunnels():
        """Start all enabled tunnel providers"""
        for provider, config in TUNNEL_PROVIDERS.items():
            if config['enabled']:
                TunnelManager.start_tunnel(provider)
    
    @staticmethod
    def start_tunnel(provider: str):
        """Start a specific tunnel provider"""
        if provider in TUNNEL_PROCESSES:
            logger.info(f"Tunnel {provider} already running")
            return
        
        config = TUNNEL_PROVIDERS.get(provider)
        if not config:
            logger.error(f"Unknown tunnel provider: {provider}")
            return
        
        try:
            process = subprocess.Popen(
                config['command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            TUNNEL_PROCESSES[provider] = process
            
            threading.Thread(
                target=TunnelManager._monitor_tunnel,
                args=(provider, process),
                daemon=True
            ).start()
            
            logger.info(f"Started tunnel: {provider}")
            
        except Exception as e:
            logger.error(f"Failed to start tunnel {provider}: {e}")
    
    @staticmethod
    def _monitor_tunnel(provider: str, process):
        """Monitor tunnel process and extract URL"""
        try:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    url_match = re.search(TUNNEL_PROVIDERS[provider]['url_pattern'], output)
                    if url_match:
                        url = url_match.group()
                        ACTIVE_TUNNELS[provider] = url
                        TunnelManager._save_tunnel_url(provider, url)
                        logger.info(f"Tunnel {provider} active at: {url}")
                        
                        socketio.emit('tunnel_update', {
                            'provider': provider,
                            'url': url,
                            'status': 'active'
                        })
        
        except Exception as e:
            logger.error(f"Error monitoring tunnel {provider}: {e}")
    
    @staticmethod
    def _save_tunnel_url(provider: str, url: str):
        """Save tunnel URL to database"""
        conn = sqlite3.connect(TUNNELS_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tunnel_urls (provider, url, status) VALUES (?, ?, 'active')
        ''', (provider, url))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_active_tunnels() -> Dict[str, str]:
        """Get all active tunnel URLs"""
        return ACTIVE_TUNNELS.copy()

class AgentMode:
    """Enhanced natural language agent mode"""
    
    @staticmethod
    def interpret_command(user_message: str) -> Optional[Tuple[str, str]]:
        """Interpret natural language and convert to command"""
        user_message_lower = user_message.lower().strip()
        
        # Check for direct command syntax first
        if user_message_lower.startswith(('/cmd ', '/terminal ', '$ ', '> ')):
            command = user_message.split(' ', 1)[1] if ' ' in user_message else ''
            return command, f"Direct command: {command}"
        
        # Natural language interpretation
        for pattern_group in COMMAND_PATTERNS:
            for pattern in pattern_group["patterns"]:
                match = re.search(pattern, user_message_lower)
                if match:
                    command = pattern_group["command"]
                    
                    # Handle pattern groups (captured text)
                    if match.groups():
                        for i, group in enumerate(match.groups(), 1):
                            command = command.replace(f'{{{i}}}', group.strip())
                    
                    return command, f"Interpreted '{user_message}' as: {pattern_group['description']}"
        
        return None, None
    
    @staticmethod 
    def execute_command(command: str, session_id: str) -> Dict[str, str]:
        """Safely execute terminal command"""
        try:
            if not AgentMode._is_safe_command(command):
                return {
                    'success': False,
                    'output': '',
                    'error': 'Command blocked for security reasons',
                    'interpretation': ''
                }
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd='/root'
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode,
                'interpretation': f"Executed: {command}"
            }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Command timeout (30s limit)',
                'interpretation': f"Timeout: {command}"
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'interpretation': f"Error: {command}"
            }
    
    @staticmethod
    def _is_safe_command(command: str) -> bool:
        """Check if command is safe to execute"""
        dangerous_patterns = [
            r'\brm\s+-rf\s+/',
            r'\bshutdown\b',
            r'\breboot\b',
            r'\bhalt\b',
            r'\bmkfs\b',
            r'\bdd\s+of=/dev/',
            r':\(\)\{.*\|\&\}:',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        
        return True

# Initialize databases
DatabaseManager.init_databases()

@app.route('/')
def index():
    """Main chat interface with dynamic models"""
    models = OllamaModelManager.get_available_models()
    if not models:
        models = OllamaModelManager.get_fallback_models()
    
    return render_template('index_enhanced_v3_1.html', 
                         models=models,
                         tunnels=TunnelManager.get_active_tunnels())

@app.route('/agent')
def agent_interface():
    """Dedicated agent mode interface"""
    return render_template('agent_interface.html')

@app.route('/learning_logs')
def learning_logs():
    """Learning logs interface"""
    logs = LearningManager.get_learning_logs()
    return render_template('learning_logs.html', logs=logs)

@app.route('/api/models')
def api_models():
    """Get available models dynamically"""
    models = OllamaModelManager.get_available_models()
    if not models:
        models = OllamaModelManager.get_fallback_models()
    return jsonify(models)

@app.route('/api/tunnels')
def api_tunnels():
    """Get active tunnel URLs"""
    return jsonify(TunnelManager.get_active_tunnels())

@app.route('/api/learning_feedback', methods=['POST'])
def api_learning_feedback():
    """Record user feedback for AI learning"""
    data = request.get_json()
    
    learning_id = LearningManager.record_learning(
        session_id=data.get('session_id'),
        user_correction=data.get('user_correction'),
        ai_mistake=data.get('ai_mistake'),
        context=data.get('context', ''),
        model_used=data.get('model_used')
    )
    
    return jsonify({'success': True, 'learning_id': learning_id})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {'msg': 'Connected to Project Omega Enhanced v3.1.0'})

@socketio.on('send_message')
def handle_message(data):
    """Handle incoming chat messages"""
    session_id = data.get('session_id')
    message = data.get('message')
    session_type = data.get('session_type', 'chat')
    model = data.get('model', 'mistral:7b-instruct')
    temperature = float(data.get('temperature', 0.7))
    max_tokens = int(data.get('max_tokens', 2048))
    thinking_mode = data.get('thinking_mode', False)
    internet_access = data.get('internet_access', True)
    system_prompt = data.get('system_prompt', '')
    
    try:
        if session_type == 'agent':
            handle_agent_session(session_id, message, data)
        else:
            handle_chat_session(session_id, message, data)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        emit('error', {'message': f'Error: {str(e)}'})

def handle_chat_session(session_id: str, message: str, data: dict):
    """Handle regular chat session"""
    model = data.get('model', 'mistral:7b-instruct')
    temperature = float(data.get('temperature', 0.7))
    max_tokens = int(data.get('max_tokens', 2048))
    thinking_mode = data.get('thinking_mode', False)
    internet_access = data.get('internet_access', True)
    system_prompt = data.get('system_prompt', '')
    
    # Enhance prompt with internet search if enabled
    if internet_access:
        enhanced_message = WebSearchManager.enhance_prompt_with_search(message)
    else:
        enhanced_message = message
    
    # Get relevant learnings
    learnings = LearningManager.get_relevant_learnings(enhanced_message, model)
    
    # Add learnings context to system prompt
    if learnings:
        learning_context = "\n\n[PREVIOUS LEARNINGS]:\n"
        for learning in learnings:
            learning_context += f"- {learning['summary']}\n"
        system_prompt += learning_context
    
    # Send message to AI model
    ai_response = send_to_ollama(enhanced_message, model, temperature, max_tokens, 
                               thinking_mode, system_prompt)
    
    # Store conversation in database
    store_message(session_id, 'user', message)
    store_message(session_id, 'assistant', ai_response)
    
    # Send response back to client
    emit('message_response', {
        'response': ai_response,
        'model': model,
        'session_type': 'chat',
        'internet_used': internet_access and 'INTERNET SEARCH RESULTS' in enhanced_message,
        'learnings_applied': len(learnings)
    })

def handle_agent_session(session_id: str, message: str, data: dict):
    """Handle agent mode session with natural language interpretation"""
    try:
        # Interpret the user's natural language message
        command, interpretation = AgentMode.interpret_command(message)
        
        if command:
            # Execute the interpreted command
            result = AgentMode.execute_command(command, session_id)
            
            # Format response with interpretation
            response = f"**Interpretation**: {interpretation}\n\n"
            response += f"**Command**: `{command}`\n\n"
            
            if result['success']:
                response += f"**Output**:\n```\n{result['output']}\n```"
                if result.get('error'):
                    response += f"\n\n**Warnings**:\n```\n{result['error']}\n```"
            else:
                response += f"**Error**:\n```\n{result['error']}\n```"
            
            emit('message_response', {
                'response': response,
                'model': 'agent-mode',
                'session_type': 'agent',
                'is_command_result': True,
                'command_success': result['success'],
                'interpretation': interpretation
            })
        else:
            # No command interpretation, provide helpful response
            response = f"""I understand you want to: "{message}"

I can help you with commands like:
• **"What is the Python version?"** → `python --version`
• **"List files"** → `ls -la`  
• **"Show current directory"** → `pwd`
• **"Check disk space"** → `df -h`
• **"Install pip package requests"** → `pip install requests`

You can also use direct commands: `/cmd python --version`

What would you like me to help you with?"""

            emit('message_response', {
                'response': response,
                'model': 'agent-mode', 
                'session_type': 'agent',
                'is_command_result': False
            })
        
        # Store in database
        store_message(session_id, 'user', message)
        store_message(session_id, 'assistant', response if 'response' in locals() else interpretation)
    
    except Exception as e:
        logger.error(f"Agent session error: {e}")
        emit('error', {'message': f'Agent error: {str(e)}'})

def send_to_ollama(message: str, model: str, temperature: float, max_tokens: int, 
                   thinking_mode: bool, system_prompt: str = '') -> str:
    """Send message to Ollama API"""
    try:
        url = f"{OLLAMA_API_URL}/api/generate"
        
        prompt = message
        if system_prompt:
            prompt = f"System: {system_prompt}\n\nUser: {message}"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get('response', 'No response received')
        else:
            return f"Error: Ollama API returned status {response.status_code}"
    
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        return f"Error communicating with Ollama: {str(e)}"

def store_message(session_id: str, role: str, content: str):
    """Store message in database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Database storage error: {e}")

if __name__ == '__main__':
    # Start tunnel providers
    logger.info("Starting Project Omega Enhanced v3.1.0...")
    TunnelManager.start_all_tunnels()
    
    # Start Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)