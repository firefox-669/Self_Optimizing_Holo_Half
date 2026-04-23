"""
A/B 测试示例

演示如何使用统计显著性检验评估进化效果
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from user_scoring.ab_testing import ABTestFramework, TestType, ab_test


def example_z_test():
    """Z-test 示例：大样本场景"""
    print("="*70)
    print("Example 1: Z-Test (Large Sample)")
    print("="*70)
    
    # 模拟数据：进化前后的用户评分
    variant_a_scores = [3.5, 3.8, 3.6, 3.9, 3.7, 3.5, 3.8, 3.6, 3.7, 3.9] * 10  # 100个样本
    variant_b_scores = [4.0, 4.2, 4.1, 4.3, 4.0, 4.1, 4.2, 4.0, 4.1, 4.3] * 10  # 100个样本
    
    framework = ABTestFramework(significance_level=0.05)
    result = framework.run_z_test(variant_a_scores, variant_b_scores)
    
    print(framework.interpret_result(result))
    print()


def example_t_test():
    """T-test 示例：小样本场景"""
    print("="*70)
    print("Example 2: T-Test (Small Sample)")
    print("="*70)
    
    # 模拟数据：小样本
    variant_a_scores = [3.5, 3.8, 3.6, 3.9, 3.7]
    variant_b_scores = [4.0, 4.2, 4.1, 4.3, 4.0]
    
    result = ab_test(variant_a_scores, variant_b_scores, test_type=TestType.T_TEST)
    
    print(f"P-value: {result.p_value:.6f}")
    print(f"Significant: {'Yes' if result.significant else 'No'}")
    print(f"Decision: {result.decision.value}")
    print()


def example_paired_t_test():
    """配对 T-test 示例：同一用户前后对比"""
    print("="*70)
    print("Example 3: Paired T-Test (Same Users Before/After)")
    print("="*70)
    
    # 模拟数据：同一组用户在进化前后的评分
    before_scores = [3.5, 3.8, 3.6, 3.9, 3.7, 3.5, 3.8]
    after_scores = [4.0, 4.2, 4.1, 4.3, 4.0, 4.1, 4.2]
    
    framework = ABTestFramework()
    result = framework.run_t_test(before_scores, after_scores, paired=True)
    
    print(framework.interpret_result(result))
    print()


def example_sample_size_calculation():
    """样本量计算示例"""
    print("="*70)
    print("Example 4: Sample Size Calculation")
    print("="*70)
    
    framework = ABTestFramework()
    
    # 计算检测 10% 提升所需的样本量
    n = framework.calculate_sample_size(
        min_detectable_effect=0.1,  # 最小可检测效应 10%
        power=0.8,                   # 统计功效 80%
        variance=1.0                 # 预期方差
    )
    
    print(f"To detect a 10% improvement with 80% power:")
    print(f"Required sample size per group: {n}")
    print(f"Total sample size needed: {n * 2}")
    print()


def example_real_scenario():
    """真实场景示例：评估技能进化效果"""
    print("="*70)
    print("Example 5: Real Scenario - Skill Evolution Evaluation")
    print("="*70)
    
    # 模拟：技能进化前的执行成功率
    before_evolution_success_rates = [
        0.75, 0.78, 0.76, 0.77, 0.75, 0.76, 0.78, 0.77, 0.76, 0.75
    ]
    
    # 模拟：技能进化后的执行成功率
    after_evolution_success_rates = [
        0.85, 0.87, 0.86, 0.88, 0.85, 0.86, 0.87, 0.85, 0.86, 0.88
    ]
    
    result = ab_test(
        before_evolution_success_rates,
        after_evolution_success_rates,
        test_type=TestType.T_TEST
    )
    
    print(f"Before Evolution: {result.variant_a_mean:.2%} success rate")
    print(f"After Evolution:  {result.variant_b_mean:.2%} success rate")
    print(f"Improvement:      {(result.variant_b_mean - result.variant_a_mean):.2%}")
    print(f"\n{framework.interpret_result(result)}")
    print()


if __name__ == "__main__":
    print("\n🧪 A/B Testing Framework Examples\n")
    
    example_z_test()
    example_t_test()
    example_paired_t_test()
    example_sample_size_calculation()
    example_real_scenario()
    
    print("="*70)
    print("✅ All examples completed!")
    print("="*70)
