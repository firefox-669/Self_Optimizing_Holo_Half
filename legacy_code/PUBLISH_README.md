# 🚀 SOHH - AI Agent 评估标准接口

> **让每个 AI Agent 都有科学的"体检报告"**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## 📋 项目简介

**SOHH (Self-Optimizing Holo Half)** 是一个**标准化的 AI Agent 评估系统**，类似于 USB 接口规范，为所有 AI Agent 提供统一的性能评估标准。

### 🎯 核心价值

- ✅ **标准化** - 统一的六维评估体系（成功率、效率、满意度、活跃度、成本、创新）
- ✅ **客观性** - 基于数据和统计学，不依赖主观判断
- ✅ **可比性** - 可以公平比较不同 Agent 系统的性能
- ✅ **透明化** - 完全公开的算法和指标定义
- ✅ **可扩展** - 松耦合架构，易于集成到任何 Agent 系统

---

## 🌟 核心功能

### 1️⃣ 标准数据采集接口 (Layer 1)

类似 USB 接口的标准化数据协议：

```python
from sohh_standard_interface import create_collector

# 创建采集器
collector = create_collector(agent_id="openhands-v1.0")

# 记录任务执行
collector.start_task(task_id="xxx", description="Create Flask API")
collector.end_task(task_id="xxx", success=True, tokens_used=1500)
collector.record_feedback(task_id="xxx", satisfaction_score=4.5)

# 提交数据
collector.submit_to_sohh()
```

**特点**:
- 🔌 即插即用，无需修改原项目代码
- 📊 统一的数据模型（TaskExecution, UserFeedback, CapabilitySnapshot）
- 💾 自动存储到 SQLite 数据库

### 2️⃣ 数据分析引擎 (Layer 2)

基于统计学的客观分析：

```python
from data_analytics_engine import DataAnalyticsEngine

engine = DataAnalyticsEngine()
report = engine.analyze(
    agent_id="openhands-v1.0",
    performance_data={'success_rate': 75.75, ...}
)

# 获取洞察
for insight in report.insights:
    print(f"{insight.title}: {insight.description}")
```

**提供**:
- 📈 趋势分析（improving/declining/stable）
- 🎯 行业基准对比
- ⭐⭐⭐⭐⭐ 评级系统
- 💡 关键洞察

### 3️⃣ 可视化报告系统

精美的 HTML/Markdown 报告：

![Report Preview](assets/report_preview.png)

**包含**:
- 📊 六维能力雷达图（Chart.js）
- 📈 历史趋势曲线
- 🧪 A/B 测试对比（统计显著性检验）
- 📋 统计摘要
- 💡 改进建议

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/firefox-669/Self_Optimizing_Holo_Half.git
cd Self_Optimizing_Holo_Half
pip install -e .
```

### 使用示例

#### 方式 1: 从 OpenHands/OpenSpace 采集数据

```bash
# 运行 OpenHands 任务并采集数据
python collect_from_agents.py --agent openhands \
    --task "Create a Flask REST API"

# 运行 OpenSpace 任务并采集数据
python collect_from_agents.py --agent openspace \
    --task "Fix Python bug"
```

#### 方式 2: 生成评估报告

```bash
cd Self_Optimizing_Holo_Half
python simple_gen.py
```

报告会生成在 `reports/` 目录，用浏览器打开即可查看。

---

## 📊 六维评估体系

| 维度 | 说明 | 权重 |
|------|------|------|
| **成功率** (Success Rate) | 任务成功执行的比例 | 20% |
| **效率提升** (Efficiency Gain) | 相对于基准的效率提升 | 15% |
| **用户满意度** (User Satisfaction) | 用户对结果的主观评价 | 20% |
| **使用活跃度** (Usage Activity) | 系统的使用频率和深度 | 15% |
| **成本效率** (Cost Efficiency) | Token 和金钱成本的控制 | 15% |
| **创新性** (Innovation) | 代码质量和解决方案创新 | 15% |

**综合评分计算**:
```
Overall = Success×0.20 + Efficiency×0.15 + Satisfaction×0.20 
        + Activity×0.15 + Cost×0.15 + Innovation×0.15
```

---

## 🔌 集成到其他 Agent 系统

### OpenHands 集成

```python
# 在 OpenHands 任务执行流程中
from sohh_standard_interface import create_collector

collector = create_collector(agent_id="openhands-v1.0")

# 任务开始时
collector.start_task(task.id, task.description)

# 任务结束时
collector.end_task(
    task.id, 
    success=result.success,
    tokens_used=result.tokens,
    cost=result.cost
)

# 提交数据
collector.submit_to_sohh()
```

### OpenSpace 集成

```python
# 在 OpenSpace MCP 服务器中
from sohh_standard_interface import create_collector

collector = create_collector(agent_id="openspace-v1.0")

# 记录技能使用
collector.record_skill_usage(
    skill_id="code-gen",
    skill_name="Code Generation",
    task_id=task_id,
    success=True,
    duration=execution_time
)
```

详见 [STANDARD_INTERFACE.md](STANDARD_INTERFACE.md) 获取完整文档。

---

## 📁 项目结构

```
Self_Optimizing_Holo_Half/
├── sohh_standard_interface.py      # Layer 1: 标准接口
├── data_analytics_engine.py        # Layer 2: 数据分析
├── user_scoring/
│   └── visualization_report.py     # 可视化报告生成器
├── collect_from_agents.py          # Agent 数据采集器
├── simple_gen.py                   # 快速报告生成
├── openhands_integration_example.py # OpenHands 集成示例
├── demo_analytics.py               # 数据分析演示
├── reports/                        # 生成的报告
└── data/
    └── holo_half.db               # SQLite 数据库
```

---

## 🎯 应用场景

### 1. Agent 性能评估
定期运行基准测试任务，生成进化报告，追踪性能变化。

### 2. A/B 测试
比较不同配置、模型或策略的效果，基于统计显著性做出决策。

### 3. 成本优化
监控 Token 使用和成本，识别优化机会。

### 4. 质量控制
跟踪代码质量、测试通过率等指标，确保输出质量。

### 5. 社区基准
建立行业标准，让不同 Agent 系统可以公平比较。

---

## 📈 示例报告

查看 `reports/` 目录中的示例报告：

- [evolution_report_20260424_140524.html](reports/evolution_report_20260424_140524.html) - 最新报告

报告包含：
- ✨ 全息进化指数
- 📊 六维雷达图
- 📈 30天趋势分析
- 🧪 A/B 测试结果
- 📋 统计摘要
- 💡 改进建议

---

## 🗺️ 路线图

详见 [ROADMAP.md](ROADMAP.md)

### ✅ 已完成
- [x] Layer 1: 标准数据采集接口
- [x] Layer 2: 数据分析引擎
- [x] 可视化报告系统
- [x] OpenHands/OpenSpace 集成示例

### 🚧 进行中
- [ ] my_direction 第2步：用真实任务生成报告
- [ ] my_direction 第3步：分享报告到社区

### 📋 未来计划
- [ ] Layer 3: AI 顾问插件（可插拔）
- [ ] 发布到 PyPI
- [ ] 推动 OpenHands/OpenSpace 官方集成
- [ ] 建立"SOHH Compatible"认证

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 如何贡献

1. **集成到你的 Agent 项目** - 添加 SOHH 支持
2. **改进接口设计** - 提出更好的 API 建议
3. **完善文档** - 帮助改进文档和示例
4. **报告问题** - 发现 bug 或提出改进建议

### 提交集成案例

如果你成功将 SOHH 集成到你的项目中，欢迎告诉我们：

```python
# 在你的项目中集成 SOHH
from sohh_standard_interface import create_collector

# ... 集成代码 ...

# 然后告诉我们！
# GitHub Issue: https://github.com/firefox-669/Self_Optimizing_Holo_Half/issues
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 💬 联系方式

- **GitHub**: https://github.com/firefox-669/Self_Optimizing_Holo_Half
- **Issues**: https://github.com/firefox-669/Self_Optimizing_Holo_Half/issues
- **Email**: [你的邮箱]

---

## 🙏 致谢

感谢以下项目的启发：
- [OpenHands](https://github.com/All-Hands-AI/OpenHands) - AI 驱动的开发
- [OpenSpace](https://github.com/HKUDS/OpenSpace) - 自进化 Agent 引擎

---

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

**🚀 让我们一起建立 AI Agent 评估的开放标准！**
