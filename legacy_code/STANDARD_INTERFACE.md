# SOHH 标准数据采集接口规范 v1.0

> **愿景**: 成为 AI Agent 评估领域的"USB 接口"标准

## 🎯 什么是 SOHH 标准接口？

SOHH (Self-Optimizing Holo Half) 标准接口是一个**开放的数据采集协议**，用于统一 AI Agent 系统的评估数据格式。

就像 USB 接口让不同厂商的设备可以互通一样，SOHH 标准接口让不同的 AI Agent 系统（OpenHands、AutoGen、LangChain 等）可以使用统一的评估体系。

## 🌟 为什么需要标准化？

### 当前问题
- ❌ 每个 AI Agent 项目有自己的评估方式
- ❌ 无法横向比较不同系统的性能
- ❌ 缺乏科学的评估标准
- ❌ 数据孤岛，无法形成生态

### 标准化带来的价值
- ✅ **统一评估标准** - 所有系统使用相同的六维评估体系
- ✅ **可比性** - 可以公平比较不同 Agent 的性能
- ✅ **生态系统** - 形成统一的评估生态
- ✅ **科学性** - 基于统计学和数据驱动的评估
- ✅ **透明度** - 完全公开的算法和指标定义

## 📐 核心设计理念

### 1. 松耦合 (Loose Coupling)
Agent 系统只需实现标准接口，无需依赖 SOHH 的内部实现。

```python
# Agent 系统只需要导入标准接口
from sohh_standard_interface import SOHHDataCollector

# 创建采集器
collector = SOHHDataCollector(agent_id="my-agent-v1.0")

# 记录数据
collector.start_task(...)
collector.end_task(...)
collector.submit_to_sohh()
```

### 2. 可扩展 (Extensibility)
支持自定义字段和扩展维度，满足不同场景需求。

```python
# 添加自定义元数据
collector.start_task(
    task_id="xxx",
    description="...",
    metadata={
        "custom_field_1": "value1",
        "custom_field_2": "value2"
    }
)
```

### 3. 向后兼容 (Backward Compatibility)
新版本接口兼容旧版本数据，保证生态稳定。

## 🔧 快速开始

### 安装

```bash
# 方式 1: 直接复制文件
cp sohh_standard_interface.py your_project/

# 方式 2: 通过 pip (未来发布到 PyPI)
pip install sohh-standard-interface
```

### 基本使用

```python
from sohh_standard_interface import create_collector

# 1. 创建采集器
collector = create_collector(
    agent_id="openhands-v1.0",
    project_id="my-project"
)

# 2. 记录任务执行
collector.start_task(
    task_id="task-001",
    description="Create a Flask API"
)

# ... 执行任务 ...

collector.end_task(
    task_id="task-001",
    success=True,
    tokens_used=1500,
    cost=0.003,
    code_quality_score=0.85
)

# 3. 记录用户反馈
collector.record_feedback(
    task_id="task-001",
    satisfaction_score=4.5,
    feedback_text="Great code quality!"
)

# 4. 提交数据
collector.submit_to_sohh(db_path="data/holo_half.db")
```

## 📊 六维评估体系

SOHH 标准接口采用**六维能力评估模型**：

| 维度 | 说明 | 权重 |
|------|------|------|
| **成功率** (Success Rate) | 任务成功执行的比例 | 20% |
| **效率提升** (Efficiency Gain) | 相对于基准的效率提升 | 15% |
| **用户满意度** (User Satisfaction) | 用户对结果的主观评价 | 20% |
| **使用活跃度** (Usage Activity) | 系统的使用频率和深度 | 15% |
| **成本效率** (Cost Efficiency) | Token 和金钱成本的控制 | 15% |
| **创新性** (Innovation) | 代码质量和解决方案创新 | 15% |

### 综合评分计算

```
Overall Score = 
    Success Rate × 0.20 +
    Efficiency Gain × 0.15 +
    User Satisfaction × 0.20 +
    Usage Activity × 0.15 +
    Cost Efficiency × 0.15 +
    Innovation × 0.15
```

## 🚀 集成示例

### OpenHands 集成

参考 `openhands_integration_example.py` 文件，展示了如何将 OpenHands 的执行数据通过标准接口采集。

关键集成点：
1. 在任务调度器中初始化 `SOHHDataCollector`
2. 在任务开始时调用 `start_task()`
3. 在任务结束时调用 `end_task()`
4. 收集用户反馈时调用 `record_feedback()`
5. 定期调用 `submit_to_sohh()` 提交数据

### 其他 Agent 系统

任何 AI Agent 系统都可以按照以下步骤集成：

1. **导入标准接口**
   ```python
   from sohh_standard_interface import SOHHDataCollector
   ```

2. **在合适的位置插入采集点**
   - 任务开始/结束
   - 技能/工具使用
   - 用户交互/反馈

3. **定期提交数据**
   ```python
   collector.submit_to_sohh()
   ```

## 📁 数据结构

### TaskExecution (任务执行)

```python
{
    "task_id": "唯一标识",
    "agent_id": "Agent 标识",
    "project_id": "项目标识",
    "description": "任务描述",
    "status": "pending|running|success|failed|timeout|cancelled",
    "start_time": "ISO 8601 时间",
    "end_time": "ISO 8601 时间",
    "duration_seconds": 执行时长,
    "success": true/false,
    "tokens_used": Token 数量,
    "cost": 成本（美元）,
    "iterations": 迭代次数,
    "code_quality_score": 代码质量 0-1,
    "test_pass_rate": 测试通过率 0-1
}
```

### UserFeedback (用户反馈)

```python
{
    "feedback_id": "唯一标识",
    "task_id": "关联任务ID",
    "satisfaction_score": 满意度 0-5,
    "feedback_text": "反馈文本",
    "would_recommend": true/false
}
```

### CapabilitySnapshot (能力快照)

```python
{
    "snapshot_id": "唯一标识",
    "agent_id": "Agent 标识",
    "timestamp": "ISO 8601 时间",
    "success_rate": 0-100,
    "efficiency_gain": 0-100,
    "user_satisfaction": 0-100,
    "usage_activity": 0-100,
    "cost_efficiency": 0-100,
    "innovation": 0-100,
    "overall_score": 0-100
}
```

## 🌍 生态系统愿景

### 第一阶段：建立标准 (已完成 ✅)
- [x] 定义标准接口规范
- [x] 提供参考实现 (SOHH)
- [x] 编写集成文档和示例

### 第二阶段：推广采用 (进行中 ⏳)
- [ ] OpenHands 官方集成
- [ ] AutoGen 集成
- [ ] LangChain 集成
- [ ] 其他主流 Agent 框架集成

### 第三阶段：形成生态 (未来 🚀)
- [ ] 建立统一的评估平台
- [ ] 发布基准测试数据集
- [ ] 举办 Agent 能力竞赛
- [ ] 形成行业标准

## 🤝 如何贡献

我们欢迎任何形式的贡献：

1. **集成到其他 Agent 系统** - 为你的项目添加 SOHH 支持
2. **改进接口设计** - 提出更好的 API 设计建议
3. **完善文档** - 帮助改进文档和示例
4. **报告问题** - 发现 bug 或提出改进建议

### 提交集成案例

如果你成功将 SOHH 集成到你的项目中，欢迎提交案例：

```python
# 在你的项目中
from sohh_standard_interface import SOHHDataCollector

# ... 集成代码 ...

# 然后告诉我们！
# GitHub Issue: https://github.com/firefox-669/Self_Optimizing_Holo_Half/issues
```

## 📚 相关资源

- **标准接口实现**: `sohh_standard_interface.py`
- **OpenHands 集成示例**: `openhands_integration_example.py`
- **报告生成器**: `simple_gen.py`
- **可视化报告**: `reports/` 目录

## 📄 许可证

本项目采用 MIT 许可证，可以自由使用和修改。

## 💬 联系方式

- GitHub: https://github.com/firefox-669/Self_Optimizing_Holo_Half
- Issues: https://github.com/firefox-669/Self_Optimizing_Holo_Half/issues

---

**让我们一起建立 AI Agent 评估的开放标准！** 🚀
