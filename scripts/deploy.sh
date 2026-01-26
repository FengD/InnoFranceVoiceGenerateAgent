#!/bin/bash

# Qwen3-TTS Inno France 部署脚本

set -e  # 遇到错误时退出

echo "========================================="
echo "Qwen3-TTS Inno France 部署脚本"
echo "========================================="

# 检查是否安装了conda
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到conda，请先安装Anaconda或Miniconda"
    exit 1
fi

# 创建conda环境
echo "1. 创建conda环境..."
conda env update -f environment.yml
echo "   conda环境创建完成"

# 激活环境
echo "2. 激活conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate qwen3-tts

# 安装包
echo "3. 安装Qwen3-TTS Inno France..."
pip install -e .

echo "4. 验证安装..."
python -c "import qwen3_tts_inno_france; print('安装验证成功')"

echo "========================================="
echo "部署完成！"
echo "========================================="
echo "使用说明:"
echo "1. 激活环境: source $(conda info --base)/etc/profile.d/conda.sh && conda activate qwen3-tts"
echo "2. 启动API服务: ./scripts/start_api.sh"
echo "3. 启动Web应用: ./scripts/start_webapp.sh"
echo "========================================="