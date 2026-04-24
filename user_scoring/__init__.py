"""
用户行为采集与 A/B 测试模块

负责采集、存储和查询用户在 OpenHands/OpenSpace 中的行为数据
提供科学的 A/B 测试框架（Z-test / T-test）
为评分引擎提供数据支持
"""

from .behavior_tracker import UserBehaviorTracker
from .event_logger import EventLogger
from .metrics_calculator import MetricsCalculator
from .database import DatabaseManager, init_db
from .ab_testing import ABTestFramework, ABTestResult, TestType, Decision, ab_test
from .visualization_report import VisualizationReportGenerator

__all__ = [
    "UserBehaviorTracker",
    "EventLogger", 
    "MetricsCalculator",
    "DatabaseManager",
    "init_db",
    "ABTestFramework",
    "ABTestResult",
    "TestType",
    "Decision",
    "ab_test",
    "VisualizationReportGenerator"
]
