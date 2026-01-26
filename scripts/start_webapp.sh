#!/bin/bash

# Qwen3-TTS Inno France WebApp 启动脚本

# 激活conda环境
echo "激活conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate qwen3-tts

# 设置环境变量
export ATTN_IMPLEMENTATION=sdpa
export DEVICE=cuda:0
export WEBAPP_PORT=${WEBAPP_PORT:-8000}

# 启动Web应用
echo "启动Qwen3-TTS Web应用..."
echo "访问地址: http://localhost:$WEBAPP_PORT"

python -m qwen3_tts_inno_france.webapp