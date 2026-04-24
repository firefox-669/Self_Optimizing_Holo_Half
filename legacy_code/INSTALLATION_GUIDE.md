# Self_Optimizing_Holo_Half - 完整安装和启动指南

> **重要**：本文档详细说明所有前置条件和启动步骤，确保你可以成功运行项目。

---

## 📋 前置条件检查清单

在开始之前，请确保以下条件满足：

### ✅ 必需的软件

- [ ] **Python 3.10+** 已安装
- [ ] **pip** 已安装并更新到最新版本
- [ ] **Git** 已安装（用于克隆仓库）

### ✅ 必需的外部服务（至少选择一个）

#### 选项 A：使用 OpenHands（推荐）
- [ ] OpenHands 服务正在运行
- [ ] 访问地址：`http://localhost:3000`
- [ ] 测试命令：`curl http://localhost:3000/api/status`

**如何启动 OpenHands：**
```bash
# 方法 1：使用 Docker（推荐）
docker run -d -p 3000:3000 ghcr.io/all-hands-ai/openhands:latest

# 方法 2：从源码运行
git clone https://github.com/All-Hands-AI/OpenHands.git
cd OpenHands
pip install -e .
openhands start --port 3000
```

#### 选项 B：使用 OpenSpace
- [ ] OpenSpace 已安装
- [ ] 访问地址：`http://localhost:8000`（如果使用 API 模式）

**如何安装 OpenSpace：**
```bash
pip install -e git+https://github.com/HKUDS/OpenSpace.git
```

### ✅ LLM API Key（必需）

项目需要 LLM 来进行分析和决策：

- [ ] **OpenAI API Key**（推荐）或
- [ ] **Anthropic API Key** 或
- [ ] 其他兼容 OpenAI 格式的 LLM API

**获取 API Key：**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

---

## 🚀 快速启动（5 分钟）

### 步骤 1：克隆项目

```bash
git clone https://github.com/firefox-669/Self_Optimizing_Holo_Half.git
cd Self_Optimizing_Holo_Half
```

### 步骤 2：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 3：配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# Windows: notepad .env
# Mac/Linux: nano .env
```

**.env 文件必填项：**
```env
# LLM API Key（必须填写）
LLM_API_KEY=sk-your-api-key-here

# OpenHands 地址（如果使用 OpenHands）
OPENHANDS_API_URL=http://localhost:3000

# 或者 OpenSpace 地址（如果使用 OpenSpace）
OPENSPACE_API_URL=http://localhost:8000
```

### 步骤 4：初始化数据库

```bash
python user_scoring/database.py
```

预期输出：
```
✅ Database initialized at data/holo_half.db
Database schema created successfully!
```

### 步骤 5：运行测试（可选但推荐）

```bash
# 测试 A/B 测试框架
python test_ab_testing.py

# 测试主程序
python main.py --test
```

### 步骤 6：启动项目

#### 模式 1：普通模式（生产环境）

```bash
python main.py --mode normal
```

#### 模式 2：进化模式（立即执行一次进化循环）

```bash
python main.py --mode evolution
```

#### 模式 3：自动模式（每天自动执行）⭐ 文章描述的模式

```bash
python main.py --auto
```

**自动模式说明：**
- ⏰ 每天凌晨 2:00 自动执行
- 🔄 每次执行做三件事：
  1. 📰 抓资讯（GitHub + RSS）
  2. 🧠 用大模型分析
  3. 📊 A/B 测试 + 6维评分 → 自动决策
- ⏳ 后台持续运行，按 Ctrl+C 停止

---

## 🔍 验证安装成功

### 检查点 1：依赖安装

```bash
python -c "import aiohttp, pydantic, scipy, schedule; print('✅ All dependencies installed')"
```

### 检查点 2：A/B 测试框架

```bash
python examples/ab_test_example.py
```

应该看到 5 个示例成功运行。

### 检查点 3：数据库初始化

```bash
ls data/holo_half.db  # Linux/Mac
dir data\holo_half.db  # Windows
```

文件应该存在。

### 检查点 4：主程序启动

```bash
python main.py --test
```

应该看到所有测试通过。

---

## 📖 使用示例

### 示例 1：手动执行进化循环

```python
from core.engine import SelfOptimizingEngine
import asyncio

async def main():
    async with SelfOptimizingEngine(workspace=".") as engine:
        # 运行进化循环
        result = await engine.run_self_evolution_cycle()
        
        print(f"Status: {result['status']}")
        print(f"Suggestions: {len(result.get('suggestions', []))}")

asyncio.run(main())
```

### 示例 2：使用 A/B 测试评估效果

```python
from user_scoring.ab_testing import ABTestFramework

framework = ABTestFramework()

# 进化前后的用户评分
before = [3.5, 3.6, 3.7, 3.5, 3.8]
after = [4.0, 4.1, 4.2, 4.0, 4.3]

result = framework.run_t_test(before, after)
print(framework.interpret_result(result))
```

### 示例 3：启动自动调度器

```bash
# 终端 1：启动自动进化
python main.py --auto

# 系统会每天凌晨 2:00 自动执行进化循环
# 保持终端运行，或部署到服务器
```

---

## 🛠️ 常见问题

### Q1: 提示 "OpenHands not connected"

**原因**：OpenHands 服务未启动

**解决**：
```bash
# 启动 OpenHands
docker run -d -p 3000:3000 ghcr.io/all-hands-ai/openhands:latest

# 验证服务
curl http://localhost:3000/api/status
```

### Q2: 提示 "ModuleNotFoundError: No module named 'scipy'"

**原因**：依赖未正确安装

**解决**：
```bash
pip install -r requirements.txt
```

### Q3: 自动模式不执行

**原因**：程序被终止或电脑休眠

**解决**：
- 部署到服务器（推荐）
- 或使用任务计划程序（Windows）/ cron（Linux/Mac）

**Linux/Mac 使用 cron：**
```bash
# 编辑 crontab
crontab -e

# 添加每日凌晨 2 点执行
0 2 * * * cd /path/to/Self_Optimizing_Holo_Half && python main.py --mode evolution >> logs/evolution.log 2>&1
```

**Windows 使用任务计划程序：**
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器：每天 02:00
4. 操作：启动程序 `python.exe`
5. 参数：`main.py --mode evolution`
6. 起始于：`H:\OpenSpace-main\OpenSpace-main\Self_Optimizing_Holo_Half`

### Q4: LLM API 调用失败

**原因**：API Key 无效或余额不足

**解决**：
1. 检查 `.env` 中的 `LLM_API_KEY`
2. 验证 API Key 有效性
3. 检查账户余额

---

## 📊 监控和日志

### 查看日志

```bash
# 实时查看日志
tail -f logs/evolution.log  # Linux/Mac
Get-Content logs/evolution.log -Wait  # Windows PowerShell
```

### 查看数据库

```bash
# 使用 SQLite 浏览器打开
sqlite3 data/holo_half.db

# 查询最近的进化记录
SELECT * FROM version_logs ORDER BY timestamp DESC LIMIT 10;
```

---

## 🎯 下一步

安装成功后，你可以：

1. **阅读文档**
   - [README.md](README.md) - 项目概述
   - [ARCHITECTURE_LIMITATIONS.md](ARCHITECTURE_LIMITATIONS.md) - 架构说明
   - [examples/ab_test_example.py](examples/ab_test_example.py) - A/B 测试示例

2. **自定义配置**
   - 编辑 `config.yaml` 调整参数
   - 修改 `.env` 更改 API 配置

3. **贡献代码**
   - Fork 仓库
   - 创建分支
   - 提交 Pull Request

---

## 💬 获取帮助

- **GitHub Issues**: https://github.com/firefox-669/Self_Optimizing_Holo_Half/issues
- **掘金文章**: https://juejin.cn/post/7631548637381951498

---

**祝你使用愉快！🎉**
