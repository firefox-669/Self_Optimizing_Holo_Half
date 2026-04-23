# 🚀 Git Clone 即用指南

> **目标**：实现真正的 `git clone` 后即可运行，无需复杂配置

---

## ⚡ 三步快速开始

### Windows 用户

```bash
# 1. 克隆项目
git clone https://github.com/firefox-669/Self_Optimizing_Holo_Half.git
cd Self_Optimizing_Holo_Half

# 2. 一键安装（自动完成所有配置）
setup.bat

# 3. 运行演示（无需任何外部服务）
python demo.py
```

### Linux/Mac 用户

```bash
# 1. 克隆项目
git clone https://github.com/firefox-669/Self_Optimizing_Holo_Half.git
cd Self_Optimizing_Holo_Half

# 2. 一键安装
chmod +x setup.sh
./setup.sh

# 3. 运行演示
python3 demo.py
```

---

## ✅ 一键安装脚本做了什么？

`setup.bat` / `setup.sh` 会自动完成：

1. ✅ **检查环境**
   - Python 版本 >= 3.10
   - pip 已安装

2. ✅ **安装依赖**
   - 从 requirements.txt 安装所有必需包
   - 包括：aiohttp, pydantic, scipy, schedule, numpy 等

3. ✅ **初始化数据库**
   - 创建 SQLite 数据库
   - 建立所有必需的表结构

4. ✅ **配置文件**
   - 从 .env.example 复制生成 .env
   - 提示用户填写 API Key

5. ✅ **运行测试**
   - 验证 A/B 测试框架
   - 确保所有功能正常

**整个过程全自动，无需手动操作！**

---

## 🎯 运行演示（零配置）

```bash
python demo.py
```

演示内容包括：

### 1. A/B 测试框架
- ✅ Z-test 统计检验
- ✅ T-test 统计检验
- ✅ 自动决策引擎
- ✅ 效应量分析

### 2. 6维评分系统
- ✅ Usage Activity（使用活跃度）
- ✅ Success Rate（成功率）
- ✅ Efficiency Gain（效率提升）
- ✅ User Satisfaction（用户满意度）
- ✅ Cost Efficiency（成本效率）
- ✅ Innovation（创新性）

### 3. 版本控制
- ✅ 快照管理
- ✅ 一键回退
- ✅ Git 集成

### 4. 自动调度器
- ✅ 每日定时执行
- ✅ 三件事自动化

**演示完全独立，不需要 OpenHands 或 OpenSpace！**

---

## 🔧 完整功能启动（需要配置）

如果你想使用完整功能（集成 OpenHands/OpenSpace）：

### 步骤 1：编辑 .env 文件

```bash
# Windows
notepad .env

# Linux/Mac
nano .env
```

填入你的配置：

```env
# LLM API Key（必须）
LLM_API_KEY=sk-your-openai-key-here

# OpenHands（可选，如果需要任务执行）
OPENHANDS_API_URL=http://localhost:3000

# OpenSpace（可选，如果需要技能进化）
OPENSPACE_API_URL=http://localhost:8000
```

### 步骤 2：启动服务（可选）

**如果使用 OpenHands：**
```bash
docker run -d -p 3000:3000 ghcr.io/all-hands-ai/openhands:latest
```

**如果使用 OpenSpace：**
```bash
pip install -e git+https://github.com/HKUDS/OpenSpace.git
```

### 步骤 3：选择模式启动

```bash
# 模式 1：普通模式（生产环境）
python main.py --mode normal

# 模式 2：进化模式（立即执行一次）
python main.py --mode evolution

# 模式 3：自动模式（每天自动执行）⭐ 推荐
python main.py --auto
```

---

## 📊 验证安装成功

### 方法 1：运行演示

```bash
python demo.py
```

应该看到所有演示成功运行。

### 方法 2：运行测试

```bash
python test_ab_testing.py
```

应该输出：
```
✅ All tests passed! A/B Testing Framework is working!
```

### 方法 3：检查数据库

```bash
# 查看数据库文件是否存在
ls data/holo_half.db      # Linux/Mac
dir data\holo_half.db     # Windows
```

---

## ❓ 常见问题

### Q1: 提示 "Python not found"

**解决：**
- Windows: 从 https://www.python.org/downloads/ 下载安装
- Linux: `sudo apt install python3 python3-pip`
- Mac: `brew install python3`

### Q2: 提示 "ModuleNotFoundError"

**解决：**
```bash
# 重新安装依赖
pip install -r requirements.txt

# 或者使用 setup 脚本
setup.bat       # Windows
./setup.sh      # Linux/Mac
```

### Q3: 演示运行失败

**解决：**
```bash
# 查看详细错误
python demo.py 2>&1 | more

# 检查 Python 版本
python --version  # 应该 >= 3.10

# 检查依赖
pip list | grep scipy
pip list | grep numpy
```

### Q4: 想要最简体验

**解决：**
```bash
# 只需这三步，无需任何配置
git clone https://github.com/firefox-669/Self_Optimizing_Holo_Half.git
cd Self_Optimizing_Holo_Half
python demo.py
```

---

## 🎓 学习路径

### 第 1 步：理解核心概念（5分钟）
```bash
python demo.py
```
观看 A/B 测试、评分系统、版本控制的演示。

### 第 2 步：查看示例代码（10分钟）
```bash
python examples/ab_test_example.py
```
学习如何使用 A/B 测试框架。

### 第 3 步：阅读文档（15分钟）
- README.md - 项目概述
- INSTALLATION_GUIDE.md - 详细安装指南
- VERIFY_ARTICLE_MATCH.md - 功能验证

### 第 4 步：配置完整环境（可选）
- 获取 LLM API Key
- 启动 OpenHands/OpenSpace
- 运行 `python main.py --auto`

---

## 📁 项目结构（简化版）

```
Self_Optimizing_Holo_Half/
│
├── setup.bat              # Windows 一键安装 ⭐
├── setup.sh               # Linux/Mac 一键安装 ⭐
├── demo.py                # 快速演示（零配置）⭐
│
├── main.py                # 主入口
├── requirements.txt       # 依赖列表
├── .env.example           # 配置模板
│
├── user_scoring/          # 评分和 A/B 测试
│   ├── ab_testing.py      # A/B 测试框架
│   ├── metrics_calculator.py  # 6维评分
│   └── database.py        # 数据库管理
│
├── core/                  # 核心引擎
│   ├── auto_scheduler.py  # 自动调度器
│   └── engine.py          # 主引擎
│
├── version_control/       # 版本控制
├── examples/              # 使用示例
└── docs/                  # 文档
```

---

## 🎯 核心特性总结

| 特性 | 是否需要配置 | 说明 |
|------|------------|------|
| **A/B 测试框架** | ❌ 不需要 | demo.py 即可演示 |
| **6维评分系统** | ❌ 不需要 | demo.py 即可演示 |
| **版本控制** | ❌ 不需要 | demo.py 即可演示 |
| **自动调度器** | ❌ 不需要 | demo.py 展示概念 |
| **OpenHands 集成** | ✅ 需要配置 | 需要启动服务 |
| **OpenSpace 集成** | ✅ 需要配置 | 需要安装包 |
| **LLM 分析** | ✅ 需要 API Key | 在 .env 中配置 |

---

## 💡 最佳实践

### 对于初学者
```bash
# 只需运行演示，了解核心功能
git clone https://github.com/firefox-669/Self_Optimizing_Holo_Half.git
cd Self_Optimizing_Holo_Half
python demo.py
```

### 对于开发者
```bash
# 完整安装，开始开发
./setup.sh  # 或 setup.bat
python main.py --mode normal
```

### 对于生产环境
```bash
# 配置完整环境，启动自动模式
# 1. 编辑 .env 填入 API Keys
# 2. 启动 OpenHands/OpenSpace
# 3. 部署到服务器
python main.py --auto
```

---

## 🚀 总结

**Self_Optimizing_Holo_Half 现在真正支持 "git clone 即用"！**

- ✅ 一键安装脚本（setup.bat / setup.sh）
- ✅ 零配置演示（demo.py）
- ✅ 完整的测试套件
- ✅ 详细的文档

**只需 3 个命令即可开始：**
```bash
git clone https://github.com/firefox-669/Self_Optimizing_Holo_Half.git
cd Self_Optimizing_Holo_Half
python demo.py
```

**享受自进化 AI Agent 的魅力！** 🎉
