# 🚀 Self-Optimizing Holo Half (SOHH)

> **AI Agent 全息进化评估引擎 v2.1**  
> *科学评估 · 透明诊断 · 链路可视化*

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-2.1-green.svg)](https://github.com/firefox-669/Self_Optimizing_Holo_Half/releases)
[![Article](https://img.shields.io/badge/知乎-技术文章-orange.svg)](https://zhuanlan.zhihu.com/p/2031843328103335693)

---

## 📖 项目简介

**SOHH (Self-Optimizing Holo Half)** 是一个专业的 AI Agent 评估与诊断引擎。它不再试图"替代"Agent 执行任务，而是专注于为任何 AI Agent 系统提供**标准化的能力评估、透明化的诊断报告和科学的进化建议**。

### 🎯 核心定位

> **"我们不是医生替病人锻炼，而是提供专业的体检报告和进化处方。"**

SOHH 通过采集 Agent 的执行数据，生成包含六维能力雷达图、历史趋势分析、A/B 测试对比的专业 HTML 报告，帮助开发者精准定位 Agent 的能力短板并制定优化策略。

### 📝 详细介绍

👉 **[知乎技术文章：SOHH - 为AI Agent打造的科学评估框架](https://zhuanlan.zhihu.com/p/2031843328103335693)**

---

## ✨ 核心特性

### 📊 六维能力雷达图
基于成功率、效率提升、用户满意度、使用活跃度、成本效率和创新性六个维度，全方位评估 Agent 的综合表现。

### 🔍 透明化算法
所有评分逻辑公开可查，拒绝"黑盒"评分。每个分数都有明确的计算依据和基准线说明。

### 💡 智能进化建议
基于数据分析自动生成针对性的优化建议，包括 Prompt 调优方向、技能补全优先级等。

### 🧪 A/B 测试框架
支持科学验证不同策略（如保守 vs 激进）的效果差异，提供 p-value 统计显著性检验。

### 📈 历史趋势追踪
按天聚合能力快照，可视化展示 Agent 的长期进化轨迹（需积累多日数据）。

### 🔗 执行链路可视化 (v2.1 New!)
点击报告中的任务行，即可弹出模态框查看 Agent 的完整执行轨迹：
- **用户指令**：任务的原始描述
- **Agent 思考**：每一步的决策逻辑与反思
- **工具调用**：具体的参数与命令细节
- **环境反馈**：真实的执行结果与报错信息

### 🌐 跨平台兼容
通过标准化接口 (`sohh_standard_interface.py`)，支持与 OpenSpace、OpenHands 等主流 Agent 框架无缝集成。

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 2️⃣ 配置环境变量

复制 `.env.example` 为 `.env` 并填写你的 LLM API 配置：

```bash
cp .env.example .env
```

示例配置（以中国移动 MaaS 平台为例）：
```env
OPENAI_BASE_URL=https://maas.cmchina.com/v1
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=openai/minimax-m25
```

### 3️⃣ 运行基准测试

```bash
python run_openspace_benchmark.py
```

这将自动执行 15 个多样化任务（涵盖简单、中等、复杂难度），并将结果存入 SQLite 数据库。

### 4️⃣ 生成评估报告

```bash
python -c "from user_scoring.visualization_report import VisualizationReportGenerator; r = VisualizationReportGenerator(); r.generate_comprehensive_report()"
```

生成的 HTML 报告将保存在 `reports/` 目录下，直接用浏览器打开即可查看。

---

## 📂 项目结构

```
Self_Optimizing_Holo_Half/
├── sohh_standard_interface.py      # 标准化数据采集接口（核心）
├── user_scoring/                   # 评估引擎
│   ├── database.py                 # SQLite 数据库管理
│   └── visualization_report.py     # HTML 报告生成器
├── run_openspace_benchmark.py      # OpenSpace 基准测试脚本
├── examples/                       # 示例与演示
│   ├── demo.py                     # 基础用法演示
│   └── openspace_real_assessment.html  # 真实评估报告样例
├── reports/                        # 生成的评估报告（gitignore）
├── data/                           # 本地数据库（gitignore）
├── legacy_code/                    # 旧系统代码归档
└── archive/                        # 已废弃模块归档
```

---

## 📊 报告样例

![六维雷达图](assets/radar_chart_preview.png)
*六维能力雷达图展示 Agent 的均衡性*

![历史趋势](assets/trend_chart_preview.png)
*历史趋势分析（需积累多日数据）*

查看完整样例：[examples/openspace_real_assessment.html](examples/openspace_real_assessment.html)

---

## 🔧 集成指南

### 与 OpenSpace 集成

```python
from sohh_standard_interface import SOHHDataCollector

# 初始化采集器
collector = SOHHDataCollector(agent_id="openspace_v1")

# 开始任务
task = collector.start_task(description="生成斐波那契数列函数")

# ... 执行你的 Agent 任务 ...

# 结束任务并提交数据
collector.end_task(
    task=task,
    success=True,
    duration=196.03,
    iterations=5,
    tokens_used=1250,
    cost=0.008
)
```

### 与 OpenHands 集成

参考 `examples/openhands_integration_example.py`

---

## 📈 版本演进

### v2.1 - Trace Visualization (2026-04-25)
- ✅ **新增执行链路可视化**：支持在 HTML 报告中点击查看任务详情
- ✅ **插件化分析架构**：新增 `plugins/openspace_analyzer.py`，支持多格式日志解析
- ✅ **深度日志挖掘**：自动关联 OpenSpace 真实日志路径，还原“指令-行动-反馈”闭环
- ✅ **稳健的数据注入**：采用 Base64 编码方案，彻底解决长文本嵌入导致的 JS 崩溃问题
- ✅ **仓库规范化**：完善 `.gitignore`，确保代码库整洁、专业

### v2.0 - Assessment Engine (2026-04-25)
- ✅ 新增 OpenSpace 真实基准测试支持
- ✅ 实现透明化 HTML 评估报告生成
- ✅ 修复数值计算逻辑（杜绝夸张百分比）
- ✅ 增加任务清单展示和指标释义
- ✅ 增加统计效力说明（置信区间、样本量要求）
- ✅ 优化 A/B 测试逻辑（动态标记优胜者）
- ✅ 归档旧系统代码至 `legacy_code/`

### v1.x - Legacy System
- 旧版自进化系统代码已归档至 `legacy_code/` 和 `archive/` 目录

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！在提交前请确保：

1. 代码符合 PEP 8 规范
2. 添加了必要的单元测试
3. 更新了相关文档

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [OpenSpace](https://github.com/...) - 强大的 AI Agent 框架
- [OpenHands](https://github.com/...) - 开源代码助手
- Chart.js - 优秀的图表渲染库

---

*本报告由 Self-Optimizing Holo Half 自动生成*  
*科学评估 · 持续进化*
