#!/usr/bin/env python3
"""
Project Omega Enhanced v3.2.0 - Perfect Chat Mode Implementation
New Features:
- Fixed model loading with proper timeout and error handling
- Autosave sessions with auto-generated names
- Default settings: blank system prompt, all modes enabled
- Fixed learning logs route
- Clear chat preserves learnings
- Improved reliability and user experience
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
app.config['SECRET_KEY'] = 'omega-enhanced-v3.2-secret-key-2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration
OLLAMA_API_URL = "http://localhost:11434"
FASTAPI_URL = "http://localhost:8000"
DATABASE_PATH = "chat_sessions.db"
LEARNINGS_DATABASE_PATH = "ai_learnings.db"
TUNNELS_DATABASE_PATH = "tunnel_providers.db"
MODEL_FETCH_TIMEOUT = 5  # seconds

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
        "patterns": [r"memory.*usage", r"ram.*usage", r"free.*memory", r"memory.*info"],
        "command": "free -h",
        "description": "Show memory usage"
    },
    {
        "patterns": [r"system.*info", r"system.*details", r"uname", r"os.*info"],
        "command": "uname -a",
        "description": "Show system information"
    },
    {
        "patterns": [r"processes", r"running.*processes", r"ps", r"what.*running"],
        "command": "ps aux",
        "description": "Show running processes"
    },
    {
        "patterns": [r"network.*info", r"ip.*address", r"ifconfig", r"network.*config"],
        "command": "ip addr show",
        "description": "Show network configuration"
    }
]

class SessionNameGenerator:
    """Generate meaningful session names based on first user message"""
    
    KEYWORDS_MAP = {
        "code": ["code", "programming", "python", "javascript", "html", "css", "function", "script"],
        "analysis": ["analyze", "analysis", "data", "statistics", "report", "insights"],
        "writing": ["write", "essay", "article", "content", "blog", "story"],
        "help": ["help", "how to", "explain", "tutorial", "guide", "assistance"],
        "research": ["research", "find", "search", "information", "study"],
        "creative": ["create", "design", "generate", "make", "build"],
        "question": ["what", "why", "how", "when", "where", "who"],
        "math": ["calculate", "solve", "math", "equation", "formula"],
        "planning": ["plan", "schedule", "organize", "strategy", "roadmap"],
        "review": ["review", "check", "evaluate", "assess", "feedback"]
    }
    
    @staticmethod
    def generate_session_name(message: str) -> str:
        """Generate a meaningful session name from the first message"""
        try:
            # Clean the message
            clean_message = re.sub(r'[^\w\s]', ' ', message.lower())
            words = clean_message.split()
            
            # Find matching categories
            categories = []
            for category, keywords in SessionNameGenerator.KEYWORDS_MAP.items():
                if any(keyword in clean_message for keyword in keywords):
                    categories.append(category)
            
            # Generate name based on categories and first few words
            if categories:
                primary_category = categories[0]
                first_words = ' '.join(words[:3])
                name = f"{primary_category.title()}: {first_words.title()}"
            else:
                # Fallback: use first few words
                first_words = ' '.join(words[:4])
                name = first_words.title() if first_words else "Chat Session"
            
            # Ensure name isn't too long
            if len(name) > 40:
                name = name[:37] + "..."
                
            return name
            
        except Exception as e:
            logger.error(f"Error generating session name: {e}")
            return f"Session {datetime.now().strftime('%H:%M')}"

class OllamaModelManager:
    """Enhanced Ollama model management with timeout and error handling"""
    
    @staticmethod
    def get_available_models() -> List[Dict]:
        """Get available models from Ollama API with improved error handling"""
        try:
            logger.info("Fetching models from Ollama API...")
            response = requests.get(
                f"{OLLAMA_API_URL}/api/tags", 
                timeout=MODEL_FETCH_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                models = []
                
                for model in data.get('models', []):
                    model_name = model.get('name', '')
                    model_size = model.get('size', 0)
                    
                    # Determine model capabilities based on name
                    supports_thinking = any(keyword in model_name.lower() 
                                         for keyword in ['wizard', 'uncensored', 'dolphin', 'llama'])
                    
                    models.append({
                        'id': model_name,
                        'name': model_name.replace(':', ' ').title(),
                        'type': 'advanced' if supports_thinking else 'standard',
                        'supports_thinking': supports_thinking,
                        'supports_internet': True,  # All models support internet
                        'size_gb': round(model_size / (1024**3), 1) if model_size else 0,
                        'description': f'Dynamic model - {round(model_size / (1024**3), 1)}GB' if model_size else 'Dynamic model'
                    })
                
                logger.info(f"Successfully loaded {len(models)} models from Ollama")
                return models
            else:
                logger.error(f"Failed to fetch models: HTTP {response.status_code}")
                return OllamaModelManager.get_fallback_models()
                
        except requests.exceptions.Timeout:
            logger.warning("Ollama API timeout, using fallback models")
            return OllamaModelManager.get_fallback_models()
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama API connection failed, using fallback models")  
            return OllamaModelManager.get_fallback_models()
        except Exception as e:
            logger.error(f"Unexpected error fetching models: {e}")
            return OllamaModelManager.get_fallback_models()
    
    @staticmethod
    def get_fallback_models() -> List[Dict]:
        """Reliable fallback models when Ollama API is unavailable"""
        logger.info("Using fallback models")
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
                'id': 'llama3.2:3b-instruct',
                'name': 'Llama 3.2 3B Instruct',
                'type': 'advanced',
                'supports_thinking': True,
                'supports_internet': True,
                'size_gb': 2.0,
                'description': 'Advanced reasoning model'
            },
            {
                'id': 'phi3:mini',
                'name': 'Phi-3 Mini',
                'type': 'standard',
                'supports_thinking': True,
                'supports_internet': True,
                'size_gb': 2.3,
                'description': 'Compact high-performance model'
            },
            {
                'id': 'qwen2:1.5b-instruct', 
                'name': 'Qwen2 1.5B Instruct',
                'type': 'standard',
                'supports_thinking': False,
                'supports_internet': True,
                'size_gb': 1.0,
                'description': 'Ultra-fast lightweight model'
            }
        ]

class DatabaseManager:
    """Enhanced database manager with improved session handling"""
    
    @staticmethod
    def init_databases():
        """Initialize all databases"""
        DatabaseManager.init_sessions_db()
        DatabaseManager.init_learnings_db()
        DatabaseManager.init_tunnels_db()
    
    @staticmethod
    def init_sessions_db():
        """Initialize chat sessions database with enhanced autosave support"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                session_type TEXT DEFAULT 'chat',
                model TEXT NOT NULL,
                system_prompt TEXT DEFAULT '',
                temperature REAL DEFAULT 0.7,
                max_tokens INTEGER DEFAULT 2048,
                thinking_mode BOOLEAN DEFAULT 1,
                internet_access BOOLEAN DEFAULT 1,
                learning_mode BOOLEAN DEFAULT 1,
                auto_saved BOOLEAN DEFAULT 1,
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
        logger.info("Sessions database initialized successfully")
    
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
        logger.info("Learnings database initialized successfully")
    
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
        logger.info("Tunnels database initialized successfully")

class WebSearchManager:
    """Handle web search for internet-enabled models"""
    
    @staticmethod
    def search_web(query: str, max_results: int = 3) -> List[Dict]:
        """Search web using DuckDuckGo API"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # DuckDuckGo instant answer API
            search_url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(search_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Add instant answer if available
                if data.get('Abstract'):
                    results.append({
                        'title': data.get('Heading', 'Instant Answer'),
                        'content': data.get('Abstract'),
                        'url': data.get('AbstractURL', ''),
                        'source': 'DuckDuckGo Instant Answer'
                    })
                
                # Add related topics
                for topic in data.get('RelatedTopics', [])[:max_results]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        results.append({
                            'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                            'content': topic.get('Text'),
                            'url': topic.get('FirstURL', ''),
                            'source': 'DuckDuckGo'
                        })
                
                return results[:max_results]
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            
        return [{'title': 'Search Failed', 'content': f'Unable to search for: {query}', 'url': '', 'source': 'Error'}]

class LearningManager:
    """Enhanced AI learning system that persists across sessions"""
    
    @staticmethod
    def record_learning(session_id: str, user_correction: str, ai_mistake: str, 
                       context: str, model_used: str) -> int:
        """Record a learning instance"""
        try:
            conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
            cursor = conn.cursor()
            
            # Generate learning summary
            learning_summary = f"User corrected: '{ai_mistake[:100]}...' with: '{user_correction[:100]}...'"
            
            cursor.execute('''
                INSERT INTO learnings (session_id, user_correction, ai_mistake, context, model_used, learning_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, user_correction, ai_mistake, context, model_used, learning_summary))
            
            learning_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded learning #{learning_id} for session {session_id}")
            return learning_id
            
        except Exception as e:
            logger.error(f"Error recording learning: {e}")
            return -1
    
    @staticmethod
    def get_relevant_learnings(context: str, model_used: str) -> List[Dict]:
        """Get relevant learnings for current context"""
        try:
            conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_correction, ai_mistake, learning_summary, applied_count
                FROM learnings
                WHERE model_used = ? OR model_used IS NULL
                ORDER BY effectiveness_score DESC, created_at DESC
                LIMIT 5
            ''', (model_used,))
            
            learnings = []
            for row in cursor.fetchall():
                learnings.append({
                    'id': row[0],
                    'user_correction': row[1],
                    'ai_mistake': row[2],
                    'learning_summary': row[3],
                    'applied_count': row[4]
                })
            
            conn.close()
            return learnings
            
        except Exception as e:
            logger.error(f"Error fetching learnings: {e}")
            return []
    
    @staticmethod
    def apply_learning(learning_id: int, session_id: str, success: bool = True):
        """Record when a learning is applied"""
        try:
            conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
            cursor = conn.cursor()
            
            # Record application
            cursor.execute('''
                INSERT INTO learning_applications (learning_id, session_id, success)
                VALUES (?, ?, ?)
            ''', (learning_id, session_id, success))
            
            # Update applied count and effectiveness
            cursor.execute('''
                UPDATE learnings 
                SET applied_count = applied_count + 1,
                    effectiveness_score = CASE 
                        WHEN ? THEN effectiveness_score + 0.1
                        ELSE effectiveness_score - 0.1
                    END
                WHERE id = ?
            ''', (success, learning_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error applying learning: {e}")
    
    @staticmethod
    def get_learning_logs(limit: int = 50) -> List[Dict]:
        """Get learning logs for display"""
        try:
            conn = sqlite3.connect(LEARNINGS_DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT l.id, l.session_id, l.user_correction, l.ai_mistake, 
                       l.context, l.model_used, l.learning_summary, l.created_at,
                       l.applied_count, l.effectiveness_score,
                       COUNT(la.id) as total_applications
                FROM learnings l
                LEFT JOIN learning_applications la ON l.id = la.learning_id
                GROUP BY l.id
                ORDER BY l.created_at DESC
                LIMIT ?
            ''', (limit,))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'id': row[0],
                    'session_id': row[1],
                    'user_correction': row[2],
                    'ai_mistake': row[3],
                    'context': row[4],
                    'model_used': row[5],
                    'learning_summary': row[6],
                    'created_at': row[7],
                    'applied_count': row[8],
                    'effectiveness_score': row[9],
                    'total_applications': row[10]
                })
            
            conn.close()
            return logs
            
        except Exception as e:
            logger.error(f"Error fetching learning logs: {e}")
            return []

class TunnelManager:
    """Manage multiple tunnel providers"""
    
    @staticmethod
    def start_tunnel(provider_name: str) -> Optional[str]:
        """Start a specific tunnel provider"""
        if provider_name not in TUNNEL_PROVIDERS:
            return None
            
        provider = TUNNEL_PROVIDERS[provider_name]
        
        try:
            logger.info(f"Starting {provider['name']} tunnel...")
            process = subprocess.Popen(
                provider['command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            TUNNEL_PROCESSES[provider_name] = process
            
            # Give the tunnel time to start
            time.sleep(3)
            
            # Try to extract URL from output
            for line in process.stdout:
                if line.strip():
                    url_match = re.search(provider['url_pattern'], line)
                    if url_match:
                        url = url_match.group(0)
                        ACTIVE_TUNNELS[provider_name] = url
                        logger.info(f"{provider['name']} tunnel active: {url}")
                        
                        # Store in database
                        TunnelManager.store_tunnel_url(provider_name, url)
                        return url
                        
        except Exception as e:
            logger.error(f"Error starting {provider['name']}: {e}")
            
        return None
    
    @staticmethod
    def store_tunnel_url(provider: str, url: str):
        """Store tunnel URL in database"""
        try:
            conn = sqlite3.connect(TUNNELS_DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO tunnel_urls (provider, url, status, created_at, last_checked)
                VALUES (?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (provider, url))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing tunnel URL: {e}")
    
    @staticmethod
    def get_active_tunnels() -> List[Dict]:
        """Get all active tunnel URLs including currently running ones"""
        tunnels = []
        
        # Add tunnels from ACTIVE_TUNNELS dictionary
        for provider, url in ACTIVE_TUNNELS.items():
            if provider in TUNNEL_PROVIDERS:
                tunnels.append({
                    'provider': provider,
                    'name': TUNNEL_PROVIDERS[provider]['name'],
                    'url': url,
                    'priority': TUNNEL_PROVIDERS[provider]['priority']
                })
        
        # Check for running serveo.net tunnel from log file
        try:
            with open('/tmp/serveo.log', 'r') as f:
                content = f.read()
                if 'serveo.net' in content:
                    lines = content.split('\n')
                    for line in lines:
                        if 'https://' in line and 'serveo.net' in line:
                            # Extract URL from line like "Forwarding HTTP traffic from https://xyz.serveo.net"
                            import re
                            url_match = re.search(r'https://[\w-]+\.serveo\.net', line)
                            if url_match:
                                serveo_url = url_match.group(0)
                                # Check if already in tunnels
                                if not any(t['url'] == serveo_url for t in tunnels):
                                    tunnels.append({
                                        'provider': 'serveo',
                                        'name': 'Serveo.net (Active)',
                                        'url': serveo_url,
                                        'priority': 1
                                    })
                                break
        except FileNotFoundError:
            pass
        
        # Check for direct RunPod IP access
        try:
            import os
            ip = os.environ.get('RUNPOD_PUBLIC_IP', '213.173.99.7')
            # Check if port 5000 is accessible
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, 5000))
                sock.close()
                if result == 0:  # Port is open
                    direct_url = f"http://{ip}:5000"
                    if not any(t['url'] == direct_url for t in tunnels):
                        tunnels.append({
                            'provider': 'direct',
                            'name': 'Direct RunPod Access',
                            'url': direct_url,
                            'priority': 5
                        })
            except:
                pass
        except:
            pass
        
        # Check for localhost.run tunnel
        try:
            result = subprocess.run(['pgrep', '-f', 'localhost.run'], capture_output=True, text=True)
            if result.returncode == 0:
                tunnels.append({
                    'provider': 'localhost_run',
                    'name': 'LocalHost.run (Active)', 
                    'url': 'Localhost.run tunnel active - check logs',
                    'priority': 2
                })
        except:
            pass
        
        return sorted(tunnels, key=lambda x: x['priority'])

class AgentCommandInterpreter:
    """Natural language command interpreter for agent mode"""
    
    @staticmethod
    def interpret_command(user_input: str) -> Optional[str]:
        """Convert natural language to shell commands"""
        user_input_lower = user_input.lower().strip()
        
        for pattern_set in COMMAND_PATTERNS:
            for pattern in pattern_set['patterns']:
                if re.search(pattern, user_input_lower):
                    logger.info(f"Matched pattern '{pattern}' -> {pattern_set['command']}")
                    return pattern_set['command']
        
        # If no pattern matches, return None
        return None
    
    @staticmethod
    def execute_command(command: str) -> Dict[str, str]:
        """Execute shell command safely"""
        try:
            logger.info(f"Executing command: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            return {
                'command': command,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                'command': command,
                'stdout': '',
                'stderr': 'Command timed out after 30 seconds',
                'returncode': -1,
                'success': False
            }
        except Exception as e:
            return {
                'command': command,
                'stdout': '',
                'stderr': f'Error executing command: {str(e)}',
                'returncode': -1,
                'success': False
            }

class SessionManager:
    """Enhanced session management with autosave"""
    
    @staticmethod
    def create_auto_session(first_message: str, model: str) -> str:
        """Create a new session with auto-generated name"""
        session_id = str(uuid.uuid4())
        session_name = SessionNameGenerator.generate_session_name(first_message)
        
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (
                    id, name, session_type, model, system_prompt, temperature, max_tokens,
                    thinking_mode, internet_access, learning_mode, auto_saved, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (
                session_id, session_name, 'chat', model, '', 0.7, 2048, 
                1, 1, 1, 1  # All modes enabled by default
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created auto session '{session_name}' with ID {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating auto session: {e}")
            return str(uuid.uuid4())
    
    @staticmethod
    def save_message(session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Save message to database"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (session_id, role, content, metadata, timestamp)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (session_id, role, content, json.dumps(metadata) if metadata else None))
            
            # Update session timestamp
            cursor.execute('''
                UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
    
    @staticmethod
    def clear_session_history(session_id: str, preserve_learnings: bool = True):
        """Clear session history but optionally preserve learnings"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Delete messages
            cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
            
            # Reset session updated time
            cursor.execute('''
                UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleared history for session {session_id}, learnings preserved: {preserve_learnings}")
            
        except Exception as e:
            logger.error(f"Error clearing session history: {e}")
    
    @staticmethod
    def get_sessions(limit: int = 20) -> List[Dict]:
        """Get recent sessions"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, model, created_at, updated_at,
                       (SELECT COUNT(*) FROM messages WHERE session_id = sessions.id) as message_count
                FROM sessions
                WHERE session_type = 'chat'
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'id': row[0],
                    'name': row[1],
                    'model': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'message_count': row[5]
                })
            
            conn.close()
            return sessions
            
        except Exception as e:
            logger.error(f"Error fetching sessions: {e}")
            return []

# Routes
@app.route('/')
def home():
    """Enhanced home page with perfect defaults"""
    return render_template('index_enhanced_v3_2.html')

@app.route('/chat')
def chat():
    """Chat interface"""
    return render_template('index_enhanced_v3_2.html')

@app.route('/agent')
def agent():
    """Agent mode interface"""
    return render_template('agent_interface.html')

@app.route('/learning_logs')
def learning_logs():
    """Learning logs interface - FIXED route"""
    try:
        logs = LearningManager.get_learning_logs()
        logger.info(f"Loading learning logs page with {len(logs)} entries")
        return render_template('learning_logs.html', logs=logs)
    except Exception as e:
        logger.error(f"Error loading learning logs: {e}")
        return render_template('learning_logs.html', logs=[], error=str(e))

# API Routes
@app.route('/api/models')
def api_models():
    """Get available models dynamically with improved reliability"""
    try:
        models = OllamaModelManager.get_available_models()
        logger.info(f"API returning {len(models)} models")
        return jsonify(models)
    except Exception as e:
        logger.error(f"Error in models API: {e}")
        fallback_models = OllamaModelManager.get_fallback_models()
        return jsonify(fallback_models)

@app.route('/api/tunnels')
def api_tunnels():
    """Get active tunnel URLs"""
    try:
        tunnels = TunnelManager.get_active_tunnels()
        return jsonify(tunnels)
    except Exception as e:
        logger.error(f"Error getting tunnels: {e}")
        return jsonify([])

@app.route('/api/sessions')
def api_sessions():
    """Get recent sessions for autosave functionality"""
    try:
        sessions = SessionManager.get_sessions()
        return jsonify(sessions)
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return jsonify([])

@app.route('/api/learning_feedback', methods=['POST'])
def api_learning_feedback():
    """Record user feedback for AI learning"""
    try:
        data = request.get_json()
        
        learning_id = LearningManager.record_learning(
            session_id=data.get('session_id'),
            user_correction=data.get('user_correction'),
            ai_mistake=data.get('ai_mistake'),
            context=data.get('context', ''),
            model_used=data.get('model_used')
        )
        
        return jsonify({'success': True, 'learning_id': learning_id})
        
    except Exception as e:
        logger.error(f"Error recording learning feedback: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clear_session', methods=['POST'])
def api_clear_session():
    """Clear session history while preserving learnings"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id:
            SessionManager.clear_session_history(session_id, preserve_learnings=True)
            return jsonify({'success': True, 'message': 'Session cleared, learnings preserved'})
        else:
            return jsonify({'success': False, 'error': 'No session ID provided'}), 400
            
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Socket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle incoming chat messages with enhanced autosave"""
    try:
        message = data.get('message', '').strip()
        model = data.get('model', 'mistral:7b-instruct')
        session_id = data.get('session_id')
        thinking_mode = data.get('thinking_mode', True)
        internet_access = data.get('internet_access', True)
        learning_mode = data.get('learning_mode', True)
        system_prompt = data.get('system_prompt', '').strip()
        temperature = data.get('temperature', 0.7)
        
        if not message:
            emit('error', {'message': 'Empty message received'})
            return
        
        # Auto-create session if none provided
        if not session_id:
            session_id = SessionManager.create_auto_session(message, model)
            emit('session_created', {'session_id': session_id})
        
        # Save user message
        SessionManager.save_message(session_id, 'user', message)
        
        # Get relevant learnings if learning mode is enabled
        learnings_context = ""
        if learning_mode:
            relevant_learnings = LearningManager.get_relevant_learnings(message, model)
            if relevant_learnings:
                learnings_context = "\n\nPrevious learnings to consider:\n"
                for learning in relevant_learnings[:3]:
                    learnings_context += f"- User previously corrected: {learning['user_correction'][:100]}\n"
        
        # Prepare the prompt
        enhanced_prompt = system_prompt
        if learnings_context:
            enhanced_prompt += learnings_context
        
        # Add internet search results if enabled
        if internet_access and any(keyword in message.lower() for keyword in ['latest', 'current', 'recent', 'news', 'today']):
            emit('status', {'message': 'Searching the internet...'})
            search_results = WebSearchManager.search_web(message)
            if search_results:
                internet_context = "\n\nCurrent internet information:\n"
                for result in search_results[:2]:
                    internet_context += f"- {result['title']}: {result['content'][:200]}\n"
                enhanced_prompt += internet_context
        
        # Make request to Ollama
        emit('status', {'message': 'Thinking...'})
        
        payload = {
            'model': model,
            'prompt': f"{enhanced_prompt}\n\nUser: {message}\nAssistant:",
            'stream': True,
            'options': {
                'temperature': temperature,
                'num_predict': 2048
            }
        }
        
        try:
            response = requests.post(
                f"{OLLAMA_API_URL}/api/generate",
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            token = json_response.get('response', '')
                            if token:
                                full_response += token
                                emit('chat_response', {'token': token})
                                
                            if json_response.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
                
                # Save AI response
                SessionManager.save_message(session_id, 'assistant', full_response)
                emit('message_complete', {'message': 'Response complete'})
                
            else:
                error_message = f"Model error: {response.status_code}"
                emit('error', {'message': error_message})
                
        except requests.exceptions.Timeout:
            emit('error', {'message': 'Request timed out. Please try again.'})
        except requests.exceptions.ConnectionError:
            emit('error', {'message': 'Cannot connect to AI model. Please check if Ollama is running.'})
        except Exception as e:
            emit('error', {'message': f'Unexpected error: {str(e)}'})
            
    except Exception as e:
        logger.error(f"Error in chat message handler: {e}")
        emit('error', {'message': f'Server error: {str(e)}'})

@socketio.on('agent_command')
def handle_agent_command(data):
    """Handle agent mode commands with natural language interpretation"""
    try:
        user_input = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_input:
            emit('agent_error', {'message': 'Empty command received'})
            return
        
        # Try to interpret the natural language command
        shell_command = AgentCommandInterpreter.interpret_command(user_input)
        
        if shell_command:
            emit('agent_status', {'message': f'Executing: {shell_command}'})
            result = AgentCommandInterpreter.execute_command(shell_command)
            
            # Send formatted result
            output = ""
            if result['stdout']:
                output += f"Output:\n{result['stdout']}\n"
            if result['stderr']:
                output += f"Errors:\n{result['stderr']}\n"
            
            emit('agent_response', {
                'command': shell_command,
                'output': output,
                'success': result['success'],
                'returncode': result['returncode']
            })
        else:
            # If no command pattern matches, provide helpful message
            available_commands = [pattern['description'] for pattern in COMMAND_PATTERNS]
            help_message = f"I didn't understand '{user_input}'. Try commands like:\n" + \
                          "\n".join([f"• {cmd}" for cmd in available_commands[:5]])
            
            emit('agent_response', {
                'command': user_input,
                'output': help_message,
                'success': False,
                'returncode': -1
            })
            
    except Exception as e:
        logger.error(f"Error in agent command handler: {e}")
        emit('agent_error', {'message': f'Command execution error: {str(e)}'})

def initialize_app():
    """Initialize the application and start tunnel services"""
    logger.info("Initializing Project Omega Enhanced v3.2.0...")
    
    # Initialize databases
    DatabaseManager.init_databases()
    
    # Start tunnel services in background
    def start_tunnels():
        time.sleep(2)  # Give the main app time to start
        for provider_name, config in TUNNEL_PROVIDERS.items():
            if config.get('enabled', False):
                threading.Thread(
                    target=TunnelManager.start_tunnel,
                    args=(provider_name,),
                    daemon=True
                ).start()
    
    threading.Thread(target=start_tunnels, daemon=True).start()
    
    logger.info("✅ Project Omega Enhanced v3.2.0 initialized successfully!")

if __name__ == '__main__':
    initialize_app()
    
    logger.info("🚀 Starting Project Omega Enhanced v3.2.0...")
    logger.info("🎯 Perfect Chat Mode Implementation")
    logger.info("✅ Auto-sessions with intelligent naming")
    logger.info("✅ Default settings: All modes enabled")
    logger.info("✅ Fixed model loading with timeout handling")
    logger.info("✅ Fixed learning logs route")
    logger.info("✅ Clear chat preserves learnings")
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=False,
        allow_unsafe_werkzeug=True
    )
