#!/bin/bash
# InstantDashboard Hackathon Demo Startup Script

echo "🚀 Starting InstantDashboard Demo Services..."

# Kill existing processes
pkill -f "uvicorn" 2>/dev/null
pkill -f "next dev" 2>/dev/null  
pkill -f "ngrok" 2>/dev/null

sleep 3

echo "📱 Starting Backend API..."
cd /Users/lnc/adk-samples/python/agents/data-science
poetry run python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

sleep 5

echo "🎨 Starting Frontend..."
cd /Users/lnc/adk-samples/python/agents/data-science/frontend
npm run dev &
FRONTEND_PID=$!

sleep 10

echo "🌐 Starting Ngrok Tunnel..."
cd /Users/lnc/adk-samples/python/agents/data-science
ngrok http 3000 &
NGROK_PID=$!

sleep 5

echo "✅ All services started!"
echo "📊 Backend PID: $BACKEND_PID"
echo "🎨 Frontend PID: $FRONTEND_PID" 
echo "🌐 Ngrok PID: $NGROK_PID"
echo ""
echo "🎯 Get your public URL:"
echo "curl -s http://localhost:4040/api/tunnels | python3 -c \"import sys,json; data=json.load(sys.stdin); print('🌟 JUDGES URL:', data['tunnels'][0]['public_url']) if data['tunnels'] else print('❌ No tunnel found')\"" 