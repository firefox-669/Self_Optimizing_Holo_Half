# OpenHands + SOHH Integration Guide

## 🎯 Overview

SOHH (Self-Optimizing Holo Half) provides a **standardized evaluation framework** for AI Agents. This guide shows how to integrate SOHH with OpenHands to enable scientific capability assessment.

---

## ✨ Why Integrate?

- 📊 **Six-dimensional evaluation** - Success Rate, Efficiency, Satisfaction, Activity, Cost, Innovation
- 🔍 **Transparent algorithms** - All scoring logic is open and verifiable
- 📈 **Historical trend tracking** - Monitor Agent evolution over time
- 🧪 **A/B testing** - Compare different configurations with statistical significance
- 🌐 **Cross-framework compatibility** - Same metrics for OpenHands, OpenSpace, AutoGen, etc.

---

## 🔌 Quick Start (3 Steps)

### Step 1: Install SOHH

```bash
# Option A: Clone the repository
git clone https://github.com/firefox-669/Self_Optimizing_Holo_Half.git
cd Self_Optimizing_Holo_Half
pip install -e .

# Option B: Copy the standard interface file
# Just copy sohh_standard_interface.py to your project
```

### Step 2: Add Collection Points

In your OpenHands task execution flow, add these three collection points:

```python
from sohh_standard_interface import create_collector

# Initialize collector (once at startup)
collector = create_collector(
    agent_id="openhands-v1.0",
    project_id="your-project-id"
)

# --- In your task execution function ---

def execute_task(task):
    # 1. Record task start
    collector.start_task(
        task_id=task.id,
        description=task.description,
        metadata={
            "framework": task.framework,
            "language": task.language
        }
    )
    
    try:
        # ... Your existing OpenHands task execution logic ...
        result = run_openhands_task(task)
        
        # 2. Record task end (on success)
        collector.end_task(
            task_id=task.id,
            success=True,
            tokens_used=result.tokens,
            cost=result.cost,
            iterations=result.iterations,
            code_quality_score=result.quality,
            test_pass_rate=result.test_rate
        )
        
        return result
        
    except Exception as e:
        # 3. Record task end (on failure)
        collector.end_task(
            task_id=task.id,
            success=False,
            error_message=str(e)
        )
        raise
```

### Step 3: Submit Data & Generate Reports

```python
# After completing tasks (or periodically)
collector.take_capability_snapshot()  # Capture current capability state
collector.submit_to_sohh(db_path="data/holo_half.db")

# Generate visualization report
cd Self_Optimizing_Holo_Half
python -m user_scoring.visualization_report
```

---

## 📋 Complete API Reference

### Core Methods

#### `create_collector(agent_id, project_id)`
Create a data collector instance.

```python
collector = create_collector(
    agent_id="openhands-v1.0",
    project_id="my-project"
)
```

#### `start_task(task_id, description, metadata=None)`
Record when a task starts.

```python
collector.start_task(
    task_id="task-001",
    description="Fix authentication bug in login.py",
    metadata={
        "file": "login.py",
        "difficulty": "medium"
    }
)
```

#### `end_task(task_id, success, ...)`
Record when a task ends.

```python
collector.end_task(
    task_id="task-001",
    success=True,
    tokens_used=1500,
    cost=0.003,
    iterations=3,
    duration=180.5,
    code_quality_score=0.85,
    test_pass_rate=0.92,
    error_message=None  # Only if success=False
)
```

#### `record_feedback(task_id, satisfaction_score, feedback_text)`
Record user feedback.

```python
collector.record_feedback(
    task_id="task-001",
    satisfaction_score=4.5,  # 1-5 scale
    feedback_text="Great job! Code is clean and well-tested.",
    would_recommend=True
)
```

#### `take_capability_snapshot()`
Capture current capability state (for trend analysis).

```python
snapshot = collector.take_capability_snapshot()
print(f"Overall Score: {snapshot.overall_score}")
```

#### `submit_to_sohh(db_path)`
Submit collected data to SOHH database.

```python
result = collector.submit_to_sohh(db_path="data/holo_half.db")
if result['success']:
    print(f"Submitted {result['tasks_inserted']} tasks")
```

---

## 🎨 Sample Report

After running the report generator, you'll get a beautiful HTML report with:

- ✅ Six-dimensional radar chart
- ✅ Interactive task list with execution traces
- ✅ Historical trend analysis
- ✅ A/B test comparison results

**Example**: [View Sample Report](https://github.com/firefox-669/Self_Optimizing_Holo_Half/releases/tag/v1.0.0)

---

## 💡 Integration Tips

### Where to Add Collection Points?

For OpenHands, the best places are:

1. **Task Execution Loop** - In the main agent loop where tasks are processed
2. **Skill/Tool Calls** - When calling specific skills or tools
3. **User Interaction** - When users provide feedback or ratings

### Example: OpenHands SDK Integration

```python
from openhands import Agent, Workspace
from sohh_standard_interface import create_collector

# Initialize
collector = create_collector(agent_id="openhands-sdk")
workspace = Workspace.from_dir("./my-project")
agent = Agent(model="claude-3-5-sonnet", workspace=workspace)

# Execute task with monitoring
task_id = "sdk-task-001"
collector.start_task(task_id=task_id, description="Refactor auth module")

try:
    result = agent.solve("Refactor the authentication module")
    
    collector.end_task(
        task_id=task_id,
        success=result.success,
        tokens_used=result.tokens,
        cost=result.cost,
        iterations=len(result.steps)
    )
except Exception as e:
    collector.end_task(task_id=task_id, success=False, error_message=str(e))
```

---

## 🔗 Resources

- **GitHub Repository**: https://github.com/firefox-669/Self_Optimizing_Holo_Half
- **Live Demo**: https://github.com/firefox-669/Self_Optimizing_Holo_Half/discussions/1
- **Full Example**: [examples/openhands_integration_example.py](examples/openhands_integration_example.py)
- **Standard Interface**: [sohh_standard_interface.py](sohh_standard_interface.py)

---

## 🤝 Support

If you have questions or need help with integration:

1. Check the full example: `examples/openhands_integration_example.py`
2. Run the demo: `python examples/openhands_integration_example.py`
3. View the guide: `python examples/openhands_integration_example.py --guide`
4. Open an issue on GitHub

---

## 📊 Benefits for OpenHands

1. **Scientific Evaluation** - Move beyond simple success/failure metrics
2. **User-Friendly Reports** - Beautiful visualizations for stakeholders
3. **Cross-Framework Comparison** - Compare OpenHands vs other agents objectively
4. **Zero Maintenance** - SOHH is independently maintained
5. **Community Standard** - Join the growing ecosystem of evaluated agents

---

**Ready to integrate?** Start with the 3-step quick start above! 🚀
