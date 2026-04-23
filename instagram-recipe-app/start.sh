#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== Reel Recipe ==="

# Install backend deps
echo "[1/4] Installing backend dependencies..."
cd "$ROOT/backend"
pip install -r requirements.txt -q

# Install frontend deps
echo "[2/4] Installing frontend dependencies..."
cd "$ROOT/frontend"
npm install --silent

# Build frontend
echo "[3/4] Building frontend..."
npm run build

# Start backend (serves frontend + API)
echo "[4/4] Starting server..."
cd "$ROOT/backend"

if [ -z "$GEMINI_API_KEY" ]; then
  echo "ERROR: GEMINI_API_KEY is not set."
  echo "Get a free key at https://aistudio.google.com then run:"
  echo "  export GEMINI_API_KEY=your_key_here"
  exit 1
fi

LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K[\d.]+' || hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
echo ""
echo "  App ready!"
echo "  Local:   http://localhost:8000"
echo "  Network: http://${LAN_IP}:8000"
echo ""
echo "  Share the Network URL with others on your WiFi."
echo "  Press Ctrl+C to stop."
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000
