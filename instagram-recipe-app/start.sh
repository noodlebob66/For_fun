#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== Reel Recipe ==="
echo ""

# ── 1. Check Ollama is installed ──────────────────────────────────────────────
if ! command -v ollama &>/dev/null; then
  echo "Ollama is not installed. Install it first:"
  echo ""
  echo "  Mac/Linux: curl -fsSL https://ollama.com/install.sh | sh"
  echo "  Windows:   download from https://ollama.com/download"
  echo ""
  exit 1
fi

# ── 2. Start Ollama if it's not already running ───────────────────────────────
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
  echo "Starting Ollama..."
  ollama serve &>/dev/null &
  sleep 3
fi

# ── 3. Pull model if not already downloaded ───────────────────────────────────
MODEL="${OLLAMA_MODEL:-llama3.2}"
if ! ollama list 2>/dev/null | grep -q "^${MODEL}"; then
  echo "Downloading AI model '${MODEL}' (~2 GB, one-time)..."
  ollama pull "$MODEL"
fi

# ── 4. Install backend deps ───────────────────────────────────────────────────
echo "[1/3] Installing backend dependencies..."
cd "$ROOT/backend"
pip install -r requirements.txt -q

# ── 5. Install & build frontend ───────────────────────────────────────────────
echo "[2/3] Building frontend..."
cd "$ROOT/frontend"
npm install --silent
npm run build

# ── 6. Launch ─────────────────────────────────────────────────────────────────
echo "[3/3] Starting server..."
cd "$ROOT/backend"

LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K[\d.]+' \
  || hostname -I 2>/dev/null | awk '{print $1}' \
  || echo "localhost")

echo ""
echo "  ✓ App ready!"
echo ""
echo "  This computer : http://localhost:8000"
echo "  Other devices : http://${LAN_IP}:8000"
echo ""
echo "  Open the 'Other devices' URL on your phone (must be on same WiFi)."
echo "  Bookmark it — that's your shared recipe app."
echo ""
echo "  Press Ctrl+C to stop."
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000
