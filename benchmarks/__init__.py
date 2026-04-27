"""
SOHH 基准测试模块

提供行业基准数据和性能对比功能
"""

from .industry_standards import (
    INDUSTRY_BENCHMARKS,
    FRAMEWORK_BENCHMARKS,
    get_benchmark,
    evaluate_performance_level,
    get_percentile_ranking,
    generate_benchmark_report
)
from .reliability_tests import (
    test_retest_reliability,
    cronbach_alpha,
    test_internal_consistency,
    inter_rater_agreement,
    generate_reliability_report
)

__all__ = [
    'INDUSTRY_BENCHMARKS',
    'FRAMEWORK_BENCHMARKS',
    'get_benchmark',
    'evaluate_performance_level',
    'get_percentile_ranking',
    'generate_benchmark_report',
    'test_retest_reliability',
    'cronbach_alpha',
    'test_internal_consistency',
    'inter_rater_agreement',
    'generate_reliability_report'
]
