#!/bin/bash

echo "=== Project Omega v3.2.0 - Comprehensive Test Suite ==="
echo "Testing all functionality and port 5000 access"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

pass_count=0
fail_count=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing $test_name... "
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        ((pass_count++))
    else
        echo -e "${RED}FAIL${NC}"
        ((fail_count++))
    fi
}

# Test 1: Ollama Service
run_test "Ollama Service" "pgrep -f 'ollama serve'"

# Test 2: Ollama API
run_test "Ollama API" "curl -s http://localhost:11434/api/tags"

# Test 3: Models Available
run_test "Models Installed" "[ $(ollama list 2>/dev/null | tail -n +2 | wc -l) -ge 2 ]"

# Test 4: Flask Application
run_test "Flask App Running" "pgrep -f 'app_enhanced_v3_2'"

# Test 5: Port 5000 Listening
run_test "Port 5000 Listening" "netstat -tlnp | grep :5000"

# Test 6: Local HTTP Access
run_test "Local HTTP Access" "curl -s -o /dev/null http://localhost:5000"

# Test 7: App Configuration
run_test "App Config (0.0.0.0:5000)" "grep -q \"host='0.0.0.0'\" app_enhanced_v3_2.py && grep -q 'port=5000' app_enhanced_v3_2.py"

# Test 8: Database Files
run_test "Database Files" "[ -f chat_sessions.db ] && [ -f ai_learnings.db ]"

# Test 9: Templates Directory
run_test "Templates Directory" "[ -d templates ] && [ -f templates/index.html ]"

# Test 10: Requirements File
run_test "Requirements File" "[ -f requirements_v3_2.txt ]"

echo ""
echo "=== Test Results ==="
echo -e "Passed: ${GREEN}$pass_count${NC}"
echo -e "Failed: ${RED}$fail_count${NC}"
echo "Total: $((pass_count + fail_count))"

if [ $fail_count -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "Project Omega v3.2.0 is fully functional"
    
    # Get Pod ID for proxy URL
    echo ""
    echo "=== Access Information ==="
    if [ -n "$RUNPOD_POD_ID" ]; then
        echo "🌐 RunPod Proxy URL: https://$RUNPOD_POD_ID-5000.proxy.runpod.net"
    else
        echo "🌐 RunPod Proxy URL: https://[YOUR-POD-ID]-5000.proxy.runpod.net"
        echo "   (Replace [YOUR-POD-ID] with your actual pod ID)"
    fi
    
    echo "🔗 Local Access: http://localhost:5000"
    echo "🔧 Direct Port: Expose port 5000 in RunPod console"
    
    echo ""
    echo "=== Service Status ==="
    echo "Ollama: $(pgrep -f 'ollama serve' | wc -l) process(es)"
    echo "Flask: $(pgrep -f 'app_enhanced_v3_2' | wc -l) process(es)"
    echo "Models: $(ollama list 2>/dev/null | tail -n +2 | wc -l) installed"
    
else
    echo -e "\n${RED}❌ SOME TESTS FAILED!${NC}"
    echo "Please check the following:"
    echo "1. Run ./complete_setup.sh to fix common issues"
    echo "2. Check logs: tail /tmp/ollama.log /tmp/flask.log"
    echo "3. Restart services if needed"
fi

echo ""
echo "📊 Quick Commands:"
echo "Status: ps aux | grep -E '(ollama|app_enhanced)'"
echo "Logs: tail -f /tmp/flask.log"
echo "Models: ollama list"
echo "Port: netstat -tlnp | grep :5000"

exit $fail_count
