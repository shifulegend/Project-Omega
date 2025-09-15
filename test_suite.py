#!/usr/bin/env python3
"""
Project Omega Enhanced v3.2.0 - Comprehensive Test Suite
Tests all features and functionalities to ensure everything works properly
"""

import requests
import json
import time
import subprocess
import os
import sys
from datetime import datetime

class ProjectOmegaTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        self.session = requests.Session()
        
    def log(self, test_name, status, message="", details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,  # PASS, FAIL, WARNING
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        # Print to console
        status_color = {
            "PASS": "\033[92m",  # Green
            "FAIL": "\033[91m",  # Red
            "WARNING": "\033[93m"  # Yellow
        }
        reset_color = "\033[0m"
        
        print(f"{status_color.get(status, '')}{status}{reset_color}: {test_name}")
        if message:
            print(f"  📝 {message}")
        if details:
            print(f"  📋 {details}")
        print()
    
    def test_application_accessibility(self):
        """Test if the application is accessible"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                if "Project Omega" in response.text:
                    self.log("Application Accessibility", "PASS", 
                           "Application is accessible and serving correct content")
                    return True
                else:
                    self.log("Application Accessibility", "FAIL", 
                           "Application accessible but wrong content served")
                    return False
            else:
                self.log("Application Accessibility", "FAIL", 
                       f"HTTP {response.status_code} returned")
                return False
        except Exception as e:
            self.log("Application Accessibility", "FAIL", 
                   f"Cannot connect to application: {str(e)}")
            return False
    
    def test_model_api(self):
        """Test if models API endpoint works"""
        try:
            response = self.session.get(f"{self.base_url}/api/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 4:
                    model_names = [model.get('name', '') for model in data]
                    self.log("Models API", "PASS", 
                           f"Found {len(data)} models", 
                           f"Models: {', '.join(model_names[:4])}")
                    return True
                else:
                    self.log("Models API", "WARNING", 
                           f"Only {len(data) if isinstance(data, list) else 0} models found, expected 4",
                           f"Response: {data}")
                    return False
            else:
                self.log("Models API", "FAIL", 
                       f"HTTP {response.status_code} returned")
                return False
        except Exception as e:
            self.log("Models API", "FAIL", 
                   f"Error accessing models API: {str(e)}")
            return False
    
    def test_tunnels_api(self):
        """Test if tunnels API endpoint works and shows active tunnels"""
        try:
            response = self.session.get(f"{self.base_url}/api/tunnels", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        tunnel_info = [f"{t.get('name', 'Unknown')} - {t.get('url', 'No URL')}" for t in data]
                        self.log("Tunnels API", "PASS", 
                               f"Found {len(data)} active tunnels",
                               f"Tunnels: {'; '.join(tunnel_info)}")
                        return True
                    else:
                        self.log("Tunnels API", "WARNING", 
                               "No active tunnels detected",
                               "This may be normal if tunnels are starting up")
                        return False
                else:
                    self.log("Tunnels API", "FAIL", 
                           "Invalid response format from tunnels API")
                    return False
            else:
                self.log("Tunnels API", "FAIL", 
                       f"HTTP {response.status_code} returned")
                return False
        except Exception as e:
            self.log("Tunnels API", "FAIL", 
                   f"Error accessing tunnels API: {str(e)}")
            return False
    
    def test_ollama_connectivity(self):
        """Test if Ollama service is running and accessible"""
        try:
            # Check if Ollama process is running
            result = subprocess.run(['pgrep', '-f', 'ollama serve'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                # Try to connect to Ollama API
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    model_count = len(data.get('models', []))
                    self.log("Ollama Connectivity", "PASS", 
                           f"Ollama is running with {model_count} models available")
                    return True
                else:
                    self.log("Ollama Connectivity", "FAIL", 
                           f"Ollama process running but API not responding: HTTP {response.status_code}")
                    return False
            else:
                self.log("Ollama Connectivity", "FAIL", 
                       "Ollama process not running")
                return False
        except Exception as e:
            self.log("Ollama Connectivity", "FAIL", 
                   f"Error checking Ollama: {str(e)}")
            return False
    
    def test_chat_functionality(self):
        """Test basic chat functionality"""
        try:
            # Test chat endpoint
            chat_data = {
                "message": "Hello, this is a test message",
                "model": "llama3.2:3b-instruct",
                "system_prompt": "",
                "temperature": 0.7,
                "max_tokens": 100,
                "thinking_mode": True,
                "internet_access": False,
                "learning_mode": True
            }
            
            response = self.session.post(f"{self.base_url}/chat", 
                                       json=chat_data, timeout=30)
            
            if response.status_code == 200:
                # Try to parse as JSON
                try:
                    data = response.json()
                    if data.get('response'):
                        self.log("Chat Functionality", "PASS", 
                               "Chat endpoint working and returned response",
                               f"Response length: {len(data.get('response', ''))} characters")
                        return True
                    else:
                        self.log("Chat Functionality", "FAIL", 
                               "Chat endpoint returned empty response")
                        return False
                except:
                    # If not JSON, check if we got a text response
                    if len(response.text) > 0:
                        self.log("Chat Functionality", "WARNING", 
                               "Chat endpoint working but returned non-JSON response",
                               f"Response: {response.text[:100]}...")
                        return False
                    else:
                        self.log("Chat Functionality", "FAIL", 
                               "Chat endpoint returned empty response")
                        return False
            else:
                self.log("Chat Functionality", "FAIL", 
                       f"Chat endpoint returned HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log("Chat Functionality", "FAIL", 
                   f"Error testing chat functionality: {str(e)}")
            return False
    
    def test_settings_functionality(self):
        """Test settings page functionality"""
        try:
            response = self.session.get(f"{self.base_url}/settings", timeout=10)
            if response.status_code == 200:
                if "Settings & Configuration" in response.text:
                    self.log("Settings Functionality", "PASS", 
                           "Settings page is accessible and loads correctly")
                    return True
                else:
                    self.log("Settings Functionality", "FAIL", 
                           "Settings page accessible but wrong content")
                    return False
            else:
                self.log("Settings Functionality", "FAIL", 
                       f"Settings page returned HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log("Settings Functionality", "FAIL", 
                   f"Error accessing settings page: {str(e)}")
            return False
    
    def test_learning_logs(self):
        """Test learning logs functionality"""
        try:
            response = self.session.get(f"{self.base_url}/learning-logs", timeout=10)
            if response.status_code == 200:
                if "Learning" in response.text or "logs" in response.text.lower():
                    self.log("Learning Logs", "PASS", 
                           "Learning logs page is accessible")
                    return True
                else:
                    self.log("Learning Logs", "WARNING", 
                           "Learning logs page accessible but content unclear")
                    return False
            else:
                self.log("Learning Logs", "FAIL", 
                       f"Learning logs page returned HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log("Learning Logs", "FAIL", 
                   f"Error accessing learning logs: {str(e)}")
            return False
    
    def test_system_health(self):
        """Test overall system health"""
        try:
            # Check process health
            processes = {
                "Flask App": "app_enhanced_v3_2",
                "Ollama": "ollama serve",
                "Serveo Tunnel": "serveo.net"
            }
            
            healthy_processes = 0
            process_details = []
            
            for name, process in processes.items():
                result = subprocess.run(['pgrep', '-f', process], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    healthy_processes += 1
                    process_details.append(f"{name}: Running")
                else:
                    process_details.append(f"{name}: Not Running")
            
            if healthy_processes >= 2:  # Flask + Ollama minimum
                self.log("System Health", "PASS", 
                       f"{healthy_processes}/{len(processes)} critical processes running",
                       "; ".join(process_details))
                return True
            else:
                self.log("System Health", "FAIL", 
                       f"Only {healthy_processes}/{len(processes)} critical processes running",
                       "; ".join(process_details))
                return False
        except Exception as e:
            self.log("System Health", "FAIL", 
                   f"Error checking system health: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🧪 Project Omega Enhanced v3.2.0 - Comprehensive Test Suite")
        print("=" * 60)
        print()
        
        tests = [
            self.test_application_accessibility,
            self.test_system_health,
            self.test_ollama_connectivity,
            self.test_model_api,
            self.test_tunnels_api,
            self.test_settings_functionality,
            self.test_learning_logs,
            self.test_chat_functionality
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for test in tests:
            try:
                result = test()
                # Count results based on last logged entry
                if self.results and self.results[-1]['status'] == 'PASS':
                    passed += 1
                elif self.results and self.results[-1]['status'] == 'FAIL':
                    failed += 1
                else:
                    warnings += 1
            except Exception as e:
                print(f"💥 Test {test.__name__} crashed: {str(e)}")
                failed += 1
        
        # Generate summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {len(tests)}")
        
        success_rate = (passed / len(tests)) * 100
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 Overall Status: HEALTHY - Application is working well!")
        elif success_rate >= 60:
            print("\n⚠️  Overall Status: WARNING - Some issues detected")
        else:
            print("\n❌ Overall Status: CRITICAL - Major issues found")
        
        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "passed": passed,
                "warnings": warnings,
                "failed": failed,
                "total": len(tests),
                "success_rate": success_rate
            },
            "detailed_results": self.results
        }
        
        with open('/tmp/test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: /tmp/test_report.json")
        
        return success_rate >= 80

def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print(f"🔗 Testing application at: {base_url}")
    print()
    
    tester = ProjectOmegaTester(base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
