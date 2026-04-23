# Self_Optimizing_Holo_Half

<div align="center">

**The Self-Evolving Platform for OpenHands & OpenSpace**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)]()

🔬 Scientific A/B Testing | 📊 6-Dimensional Scoring | 🔄 Dual Mode Support

</div>

---

## 🌟 Overview

Self_Optimizing_Holo_Half (SOHH) is an intelligent self-evolving platform that integrates **OpenHands** and **OpenSpace** to create a continuously improving AI agent system.

Unlike traditional static AI agents, SOHH uses:
- **Scientific A/B testing** with statistical significance tests
- **6-dimensional comprehensive scoring** system
- **Automated decision making** based on real user behavior
- **Dual-mode architecture** for production safety

---

## ✨ Key Features

### 🔬 Scientific Evaluation
- **6-Dimension Scoring System**: Usage activity, success rate, efficiency gain, user satisfaction, cost efficiency, innovation
- **A/B Testing Framework**: Z-test and t-test for statistical significance
- **Automated Decisions**: KEEP_AND_PROMOTE, KEEP, ROLLBACK based on data

### 📊 Real-time Monitoring
- **Performance Tracking**: Response time, token consumption, error rates
- **Anomaly Detection**: Automatic alerts for performance degradation
- **Trend Analysis**: Historical data visualization

### 🔄 Self-Evolution
- **Capability Gap Detection**: Identify missing features automatically
- **Skill Quality Assessment**: Multi-dimensional skill evaluation
- **Version Management**: Git-based versioning with one-click rollback

### 🎮 Production-Ready Design
- **Dual Mode**: Normal mode for stability, Evolution mode for improvement
- **User Behavior Tracking**: Explicit (1-5 stars) and implicit feedback
- **Configuration Management**: YAML + environment variables

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 Mode Management Layer                        │
│              (Normal / Evolution Mode)                       │
└──────────┬────────────────────────────┬─────────────────────┘
           │                            │
┌──────────▼──────────┐    ┌───────────▼──────────────────────┐
│   OpenHands Layer   │    │    OpenSpace Layer               │
│  • Task Execution   │◄──►│  • Skill Registry                │
│  • Code Generation  │    │  • Skill Evolution               │
└──────────┬──────────┘    └───────────┬──────────────────────┘
           │                           │
           └───────────┬───────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│            Self_Optimizing_Holo_Half Core                   │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Behavior  │  │   Scoring    │  │   A/B Testing   │   │
│  │  Tracking   │──│   Engine     │──│   Framework     │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Capability  │  │ Performance  │  │   Version       │   │
│  │  Analyzer   │  │  Monitor     │  │   Control       │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenHands running (local or remote)
- OpenSpace running (local or remote)

### Installation

```bash
# Clone the repository
git clone https://github.com/firefox-669/Self_Optimizing_Holo_Half.git
cd self-optimizing-holo-half

# Install dependencies
pip install -r requirements.txt

# Initialize database
python user_scoring/database.py
```

### Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your API keys:
```env
OPENHANDS_API_URL=http://localhost:3000
OPENSPACE_API_URL=http://localhost:8000
LLM_API_KEY=your_api_key_here
```

3. Configure `config.yaml`:
```yaml
mode: normal  # or 'evolution'

openhands:
  api_url: http://localhost:3000
  timeout: 300

openspace:
  api_url: http://localhost:8000
  skill_registry: ./skills

evolution:
  interval_hours: 24
  auto_apply: false
```

### Run Tests

```bash
# Quick test suite
python quick_test.py

# Or on Windows
run_tests.bat
```

Expected output:
```
============================================================
Test Summary
============================================================
Database                       ✅ PASSED
Behavior Tracker               ✅ PASSED
Scoring Engine                 ✅ PASSED
A/B Test Framework             ✅ PASSED
Mode Manager                   ✅ PASSED
Analyzers                      ✅ PASSED
------------------------------------------------------------
Total: 6/6 tests passed

🎉 All tests passed! Ready for GitHub release!
```

### Basic Usage

```python
from core.engine import HoloHalfEngine

# Initialize engine
engine = HoloHalfEngine()

# Switch to evolution mode
engine.set_mode("evolution")

# Run daily evolution cycle
results = await engine.run_daily_cycle()

# View results
print(f"Overall Score: {results['overall_score']}")
print(f"Recommendation: {results['recommendation']}")
```

---

## 📊 Scoring System

SOHH uses a **6-dimensional comprehensive scoring system**:

| Dimension | Weight | Metrics |
|-----------|--------|---------|
| **Usage Activity** | 25% | Call frequency, active users, growth rate, recency |
| **Success Rate** | 20% | Execution success, error rate, retry count |
| **Efficiency Gain** | 20% | Time saved, token efficiency, step reduction |
| **User Satisfaction** | 20% | Explicit rating, implicit feedback, reuse rate |
| **Cost Efficiency** | 10% | Token/task ratio, cost/value ratio |
| **Innovation** | 5% | Feature uniqueness, technical advancement, gap filling |

### Decision Thresholds

- **≥0.80**: KEEP_AND_PROMOTE - Excellent, promote widely
- **≥0.65**: KEEP - Good, keep as is
- **≥0.50**: KEEP_WITH_IMPROVEMENT - Acceptable, needs refinement
- **≥0.40**: REVIEW - Borderline, manual review needed
- **<0.40**: ROLLBACK - Poor, revert immediately

---

## 🧪 A/B Testing

SOHH includes a complete A/B testing framework with statistical validation:

```python
from evolution_engine.optimizer.ab_test_framework import ABTestFramework

# Start A/B test
framework = ABTestFramework()
config = await framework.start_ab_test(
    version_a="baseline_v1",
    version_b="candidate_v2",
    traffic_split=0.5,  # 50/50 split
    duration_days=7
)

# Route users
variant = await framework.route_request(user_id="user_123", test_id=config["test_id"])

# Evaluate results
results = await framework.evaluate_test(config["test_id"])
print(f"Decision: {results['decision']['action']}")
```

**Statistical Tests**:
- **Z-test** for proportion comparison (success rates)
- **t-test** for mean comparison (duration, tokens, ratings)
- **Confidence level**: 95%
- **Statistical power**: 80%

---

## 📁 Project Structure

```
Self_Optimizing_Holo_Half/
│
├── integrations/              # OpenHands/OpenSpace integration
│   ├── openhands/
│   │   ├── client.py          # MCP client
│   │   ├── capability_analyzer.py
│   │   ├── gap_detector.py
│   │   └── performance_monitor.py
│   └── openspace/
│       ├── client.py
│       └── skill_analyzer.py
│
├── evolution_engine/          # Intelligent evolution engine
│   ├── evaluator/
│   │   └── scoring_engine.py  # 6-dimension scoring
│   └── optimizer/
│       └── ab_test_framework.py
│
├── user_scoring/              # User behavior tracking
│   ├── database.py
│   ├── behavior_tracker.py
│   ├── event_logger.py
│   └── metrics_calculator.py
│
├── mode_management/           # Mode switching
│   └── mode_manager.py
│
├── core/                      # Core engine
│   ├── engine.py
│   └── evolution_loop.py
│
├── version_control/           # Version management
├── reporting/                 # Report generation
│
├── IMPLEMENTATION_PLAN.md     # Complete architecture
├── COMPLETION_REPORT.md       # Implementation report
├── RELEASE_CHECKLIST.md       # Release guide
├── quick_test.py              # Test suite
├── requirements.txt
└── config.yaml
```

---

## 🔧 Advanced Configuration

### Database

SOHH uses SQLite by default:

```python
from user_scoring.database import init_db

# Custom database path
init_db("/path/to/custom.db")
```

### Logging

Event logs are stored in `data/logs/`:

```python
from user_scoring.event_logger import EventLogger

logger = EventLogger()
logger.log_task_started(task_id="task_001", user_id="user_123")
```

### Performance Monitoring

```python
from integrations.openhands.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()

# Record execution
monitor.record_execution({
    "task_id": "task_001",
    "duration_seconds": 45.2,
    "tokens_used": 1234,
    "status": "success"
})

# Get health report
report = monitor.generate_health_report()
print(f"Health Score: {report['health_score']}/100")
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OpenHands](https://github.com/OpenHands/OpenHands) - AI software development agent
- [OpenSpace](https://github.com/HKUDS/OpenSpace) - Cross-agent skill sharing platform
- Contributors and early adopters

---

## 📬 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/firefox-669/Self_Optimizing_Holo_Half/issues)
- **Discussions**: [Join the community](https://github.com/firefox-669/Self_Optimizing_Holo_Half/discussions)

---

<div align="center">

**Made with ❤️ for the AI Agent Community**

⭐ Star this repo if you find it helpful!

</div>
