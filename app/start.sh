#!/bin/bash

# Start Qwen3-TTS Inno France service

echo "Starting Qwen3-TTS Inno France service..."

# Verify Python environment
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# Verify dependencies
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found"
    exit 1
fi

# Install dependencies if needed
echo "Checking Python dependencies..."
pip3 install -r requirements.txt

# Ensure FastAPI dependencies are installed
pip3 install fastapi uvicorn python-multipart

# Set environment variables
export DEVICE=${DEVICE:-cuda:0}
export WEBAPP_PORT=${WEBAPP_PORT:-8000}

# Start FastAPI app
echo "Starting FastAPI server on port: ${WEBAPP_PORT}"
uvicorn app.main:app --host 0.0.0.0 --port "${WEBAPP_PORT}" --reload