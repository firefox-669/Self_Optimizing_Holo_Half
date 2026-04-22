"""
报告系统模块
每日简报和深度分析
"""

from .daily_report import DailyReportGenerator
from .deep_analysis import DeepAnalyzer

__all__ = [
    "DailyReportGenerator",
    "DeepAnalyzer",
]