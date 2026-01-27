#!/bin/bash

# 启动Qwen3-TTS FastAPI Web应用

echo "启动Qwen3-TTS Inno France FastAPI Web应用..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到requirements.txt文件"
    exit 1
fi

# 安装依赖（如果需要）
echo "检查Python依赖..."
pip3 install -r requirements.txt

# 安装FastAPI相关依赖
pip3 install fastapi uvicorn python-multipart

# 设置环境变量
export DEVICE=${DEVICE:-cuda:0}
export WEBAPP_PORT=${WEBAPP_PORT:-8000}

# 启动FastAPI应用
echo "启动FastAPI服务器，端口: $WEBAPP_PORT"
python3 webapp_fastapi.py