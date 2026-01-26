#!/bin/bash

# Qwen3-TTS Inno France API 启动脚本

# 激活conda环境
echo "激活conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate qwen3-tts

# 设置环境变量
export ATTN_IMPLEMENTATION=sdpa
export DEVICE=cuda:0
export PORT=${PORT:-5000}

# 启动API服务
echo "启动Qwen3-TTS API服务..."
echo "访问地址: http://localhost:$PORT"

python -m qwen3_tts_inno_france.api