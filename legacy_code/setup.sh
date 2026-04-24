#!/bin/bash
# Self_Optimizing_Holo_Half - Linux/Mac 一键安装脚本
# 实现真正的 "git clone 即用"

set -e  # 遇到错误立即退出

echo "============================================================"
echo "Self_Optimizing_Holo_Half - Quick Setup"
echo "============================================================"
echo

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found! Please install Python 3.10+"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "MacOS: brew install python3"
    exit 1
fi
echo "[OK] Python found: $(python3 --version)"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "[ERROR] pip3 not found!"
    exit 1
fi
echo "[OK] pip found"
echo

# 安装依赖
echo "[1/4] Installing dependencies..."
pip3 install -r requirements.txt
echo "[OK] Dependencies installed"
echo

# 初始化数据库
echo "[2/4] Initializing database..."
python3 user_scoring/database.py
echo "[OK] Database initialized"
echo

# 创建 .env 文件
echo "[3/4] Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[OK] Created .env file from template"
    echo
    echo "[IMPORTANT] Please edit .env and add your API keys:"
    echo "  - LLM_API_KEY (required)"
    echo "  - OPENHANDS_API_URL (if using OpenHands)"
    echo "  - OPENSPACE_API_URL (if using OpenSpace)"
    echo
else
    echo "[OK] .env file already exists"
fi
echo

# 运行测试
echo "[4/4] Running tests..."
if python3 test_ab_testing.py; then
    echo "[OK] All tests passed!"
else
    echo "[WARNING] Some tests failed, but installation completed"
fi
echo

echo "============================================================"
echo "Installation Complete!"
echo "============================================================"
echo
echo "Next steps:"
echo "  1. Edit .env file with your API keys"
echo "  2. Start OpenHands service (if using): http://localhost:3000"
echo "  3. Run: python3 main.py --mode normal"
echo
echo "For more help, see INSTALLATION_GUIDE.md"
echo
