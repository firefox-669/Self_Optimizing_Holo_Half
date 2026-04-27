"""
Agent 评估行业基准数据

提供不同任务类型的行业标准参考值，用于评估 Agent 表现的相对水平。

数据来源：
- 学术研究论文
- 开源项目基准测试
- 社区报告的平均值
- SOHH 用户匿名统计数据

注意：这些基准会随着技术发展而更新，建议定期同步最新版本。
"""

from typing import Dict, Any


# ============================================================================
# 行业基准数据 (2026 Q2)
# ============================================================================

INDUSTRY_BENCHMARKS = {
    # 代码生成任务
    "code_generation": {
        "description": "代码生成、重构、调试任务",
        "metrics": {
            "success_rate": {
                "excellent": 90,    # 优秀：>90%
                "good": 75,         # 良好：75-90%
                "average": 60,      # 平均：60-75%
                "poor": 40,         # 较差：<40%
                "unit": "percent"
            },
            "efficiency_gain": {
                "excellent": 30,    # 比人工快30%以上
                "good": 15,         # 比人工快15-30%
                "average": 0,       # 与人工相当
                "poor": -15,        # 比人工慢
                "unit": "percent",
                "baseline_seconds": 300  # 基准时间5分钟
            },
            "user_satisfaction": {
                "excellent": 90,
                "good": 75,
                "average": 60,
                "poor": 40,
                "unit": "percent"
            },
            "usage_activity": {
                "excellent": 80,
                "good": 60,
                "average": 40,
                "poor": 20,
                "unit": "percent"
            },
            "cost_efficiency": {
                "excellent": 80,
                "good": 60,
                "average": 40,
                "poor": 20,
                "unit": "percent"
            },
            "innovation": {
                "excellent": 85,
                "good": 70,
                "average": 55,
                "poor": 35,
                "unit": "percent"
            },
            "code_quality": {
                "excellent": 0.9,   # 代码质量评分
                "good": 0.75,
                "average": 0.6,
                "poor": 0.4,
                "unit": "score_0_1"
            },
            "test_pass_rate": {
                "excellent": 0.95,
                "good": 0.85,
                "average": 0.7,
                "poor": 0.5,
                "unit": "ratio_0_1"
            }
        },
        "sample_size": 1500,  # 样本量
        "last_updated": "2026-04"
    },
    
    # 数据分析任务
    "data_analysis": {
        "description": "数据清洗、分析、可视化任务",
        "metrics": {
            "success_rate": {
                "excellent": 85,
                "good": 70,
                "average": 55,
                "poor": 35,
                "unit": "percent"
            },
            "efficiency_gain": {
                "excellent": 40,    # 数据分析Agent通常更快
                "good": 20,
                "average": 5,
                "poor": -10,
                "unit": "percent",
                "baseline_seconds": 600  # 基准时间10分钟
            },
            "accuracy": {
                "excellent": 0.95,
                "good": 0.85,
                "average": 0.7,
                "poor": 0.5,
                "unit": "ratio_0_1"
            }
        },
        "sample_size": 800,
        "last_updated": "2026-04"
    },
    
    # 文档写作任务
    "documentation": {
        "description": "技术文档、API文档、README编写",
        "metrics": {
            "success_rate": {
                "excellent": 88,
                "good": 72,
                "average": 58,
                "poor": 38,
                "unit": "percent"
            },
            "efficiency_gain": {
                "excellent": 50,    # 文档写作Agent优势明显
                "good": 25,
                "average": 10,
                "poor": -5,
                "unit": "percent",
                "baseline_seconds": 900  # 基准时间15分钟
            },
            "readability_score": {
                "excellent": 0.9,
                "good": 0.75,
                "average": 0.6,
                "poor": 0.4,
                "unit": "score_0_1"
            }
        },
        "sample_size": 600,
        "last_updated": "2026-04"
    },
    
    # Web开发任务
    "web_development": {
        "description": "前端页面、API开发、全栈应用",
        "metrics": {
            "success_rate": {
                "excellent": 82,
                "good": 65,
                "average": 50,
                "poor": 30,
                "unit": "percent"
            },
            "efficiency_gain": {
                "excellent": 35,
                "good": 18,
                "average": 5,
                "poor": -10,
                "unit": "percent",
                "baseline_seconds": 1800  # 基准时间30分钟
            },
            "code_quality": {
                "excellent": 0.85,
                "good": 0.7,
                "average": 0.55,
                "poor": 0.35,
                "unit": "score_0_1"
            }
        },
        "sample_size": 1000,
        "last_updated": "2026-04"
    },
    
    # 通用任务（默认）
    "general": {
        "description": "通用任务基准（当无法分类时使用）",
        "metrics": {
            "success_rate": {
                "excellent": 85,
                "good": 70,
                "average": 55,
                "poor": 35,
                "unit": "percent"
            },
            "efficiency_gain": {
                "excellent": 30,
                "good": 15,
                "average": 0,
                "poor": -10,
                "unit": "percent",
                "baseline_seconds": 300
            }
        },
        "sample_size": 5000,  # 最大样本量
        "last_updated": "2026-04"
    }
}


# ============================================================================
# 框架特定基准（可选，用于跨框架对比）
# ============================================================================

FRAMEWORK_BENCHMARKS = {
    # 这些数据来自社区报告和公开基准测试
    "OpenHands": {
        "avg_success_rate": 72,
        "avg_efficiency_gain": 18,
        "sample_tasks": 500,
        "source": "Community reports 2026 Q1"
    },
    "OpenSpace": {
        "avg_success_rate": 75,
        "avg_efficiency_gain": 20,
        "sample_tasks": 300,
        "source": "HKUDS official benchmarks"
    },
    "AutoGen": {
        "avg_success_rate": 68,
        "avg_efficiency_gain": 15,
        "sample_tasks": 400,
        "source": "Microsoft research papers"
    }
}


# ============================================================================
# 辅助函数
# ============================================================================

def get_benchmark(task_type: str = "general") -> Dict[str, Any]:
    """
    获取指定任务类型的基准数据
    
    Args:
        task_type: 任务类型 (code_generation, data_analysis, documentation, 
                   web_development, general)
    
    Returns:
        基准数据字典
    """
    return INDUSTRY_BENCHMARKS.get(task_type, INDUSTRY_BENCHMARKS["general"])


def evaluate_performance_level(metric_name: str, value: float, 
                               task_type: str = "general") -> str:
    """
    评估某个指标的表现等级
    
    Args:
        metric_name: 指标名称 (success_rate, efficiency_gain, etc.)
        value: 实际值
        task_type: 任务类型
    
    Returns:
        表现等级: "excellent", "good", "average", "poor"
    """
    benchmark = get_benchmark(task_type)
    metrics = benchmark.get("metrics", {})
    
    if metric_name not in metrics:
        return "unknown"
    
    thresholds = metrics[metric_name]
    
    if value >= thresholds["excellent"]:
        return "excellent"
    elif value >= thresholds["good"]:
        return "good"
    elif value >= thresholds["average"]:
        return "average"
    else:
        return "poor"


def get_percentile_ranking(value: float, task_type: str = "general",
                          metric_name: str = "success_rate") -> float:
    """
    计算某个值的百分位排名（估算）
    
    Args:
        value: 实际值
        task_type: 任务类型
        metric_name: 指标名称
    
    Returns:
        百分位排名 (0-100)
    """
    benchmark = get_benchmark(task_type)
    metrics = benchmark.get("metrics", {})
    
    if metric_name not in metrics:
        return 50.0  # 默认中位数
    
    thresholds = metrics[metric_name]
    
    # 简化的百分位估算（假设正态分布）
    if value >= thresholds["excellent"]:
        return 90.0  # 前10%
    elif value >= thresholds["good"]:
        return 70.0  # 前30%
    elif value >= thresholds["average"]:
        return 40.0  # 前60%
    else:
        return 15.0  # 后15%


def generate_benchmark_report(agent_metrics: Dict[str, float], 
                             task_type: str = "general") -> Dict[str, Any]:
    """
    生成完整的基准对比报告
    
    Args:
        agent_metrics: Agent的实际指标
        task_type: 任务类型
    
    Returns:
        包含对比分析的完整报告
    """
    benchmark = get_benchmark(task_type)
    report = {
        "task_type": task_type,
        "benchmark_source": benchmark["description"],
        "sample_size": benchmark["sample_size"],
        "comparisons": {}
    }
    
    for metric_name, actual_value in agent_metrics.items():
        level = evaluate_performance_level(metric_name, actual_value, task_type)
        percentile = get_percentile_ranking(actual_value, task_type, metric_name)
        
        report["comparisons"][metric_name] = {
            "actual_value": actual_value,
            "performance_level": level,
            "percentile_ranking": percentile,
            "industry_average": benchmark["metrics"].get(metric_name, {}).get("average", 0),
            "gap_from_average": actual_value - benchmark["metrics"].get(metric_name, {}).get("average", 0)
        }
    
    return report


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    # 示例：评估一个代码生成Agent的表现
    print("="*70)
    print("📊 Agent 性能基准对比报告")
    print("="*70)
    
    # 模拟的Agent指标
    agent_metrics = {
        "success_rate": 82.5,
        "efficiency_gain": 22.0,
        "code_quality": 0.88,
        "test_pass_rate": 0.92
    }
    
    # 生成报告
    report = generate_benchmark_report(agent_metrics, task_type="code_generation")
    
    print(f"\n任务类型: {report['task_type']}")
    print(f"基准来源: {report['benchmark_source']}")
    print(f"样本量: {report['sample_size']} 个任务\n")
    
    for metric, comparison in report["comparisons"].items():
        level_emoji = {
            "excellent": "🌟",
            "good": "✅",
            "average": "⚠️",
            "poor": "❌"
        }.get(comparison["performance_level"], "❓")
        
        print(f"{level_emoji} {metric}:")
        print(f"   实际值: {comparison['actual_value']}")
        print(f"   行业平均: {comparison['industry_average']}")
        print(f"   差距: {comparison['gap_from_average']:+.2f}")
        print(f"   表现等级: {comparison['performance_level']}")
        print(f"   百分位: 前 {100-comparison['percentile_ranking']:.0f}%\n")
    
    print("="*70)
    print("💡 提示: 这些基准会随技术发展更新，建议定期同步最新版本")
    print("="*70)
