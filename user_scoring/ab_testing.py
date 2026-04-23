"""
A/B 测试框架 - 统计显著性检验

实现 Z-test 和 T-test，用于评估进化效果的统计显著性
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TestType(Enum):
    """统计检验类型"""
    Z_TEST = "z_test"
    T_TEST = "t_test"


class Decision(Enum):
    """A/B 测试决策"""
    KEEP_AND_PROMOTE = "KEEP_AND_PROMOTE"  # 显著提升，推广
    KEEP = "KEEP"                          # 无显著差异，保留
    ROLLBACK = "ROLLBACK"                  # 显著下降，回退


@dataclass
class ABTestResult:
    """A/B 测试结果"""
    test_id: str
    variant_a_mean: float
    variant_b_mean: float
    p_value: float
    test_statistic: float
    significant: bool
    decision: Decision
    confidence_level: float
    sample_size_a: int
    sample_size_b: int
    effect_size: float  # Cohen's d


class ABTestFramework:
    """
    A/B 测试框架
    
    使用统计显著性检验来评估进化效果
    """
    
    def __init__(self, significance_level: float = 0.05, confidence_level: float = 0.95):
        """
        初始化 A/B 测试框架
        
        Args:
            significance_level: 显著性水平 (alpha)，默认 0.05
            confidence_level: 置信水平，默认 0.95
        """
        self.significance_level = significance_level
        self.confidence_level = confidence_level
    
    def run_z_test(
        self,
        variant_a_scores: List[float],
        variant_b_scores: List[float],
        known_variance_a: Optional[float] = None,
        known_variance_b: Optional[float] = None,
    ) -> ABTestResult:
        """
        执行 Z-test（适用于大样本或已知方差）
        
        Args:
            variant_a_scores: A 组得分列表
            variant_b_scores: B 组得分列表
            known_variance_a: A 组已知方差（可选）
            known_variance_b: B 组已知方差（可选）
        
        Returns:
            ABTestResult 测试结果
        """
        if len(variant_a_scores) < 2 or len(variant_b_scores) < 2:
            raise ValueError("Sample size too small for Z-test")
        
        # 计算均值
        mean_a = np.mean(variant_a_scores)
        mean_b = np.mean(variant_b_scores)
        
        # 计算方差（如果未提供）
        var_a = known_variance_a if known_variance_a else np.var(variant_a_scores, ddof=1)
        var_b = known_variance_b if known_variance_b else np.var(variant_b_scores, ddof=1)
        
        n_a = len(variant_a_scores)
        n_b = len(variant_b_scores)
        
        # 计算 Z 统计量
        se = np.sqrt(var_a / n_a + var_b / n_b)  # 标准误
        if se == 0:
            z_stat = 0
        else:
            z_stat = (mean_b - mean_a) / se
        
        # 计算 p 值（双尾检验）
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        # 判断显著性
        significant = p_value < self.significance_level
        
        # 计算效应量 (Cohen's d)
        pooled_std = np.sqrt((var_a + var_b) / 2)
        effect_size = (mean_b - mean_a) / pooled_std if pooled_std > 0 else 0
        
        # 做出决策
        decision = self._make_decision(mean_a, mean_b, significant, effect_size)
        
        return ABTestResult(
            test_id=f"z_test_{id(variant_a_scores)}",
            variant_a_mean=float(mean_a),
            variant_b_mean=float(mean_b),
            p_value=float(p_value),
            test_statistic=float(z_stat),
            significant=significant,
            decision=decision,
            confidence_level=self.confidence_level,
            sample_size_a=n_a,
            sample_size_b=n_b,
            effect_size=float(effect_size)
        )
    
    def run_t_test(
        self,
        variant_a_scores: List[float],
        variant_b_scores: List[float],
        paired: bool = False,
    ) -> ABTestResult:
        """
        执行 T-test（适用于小样本或未知方差）
        
        Args:
            variant_a_scores: A 组得分列表
            variant_b_scores: B 组得分列表
            paired: 是否为配对样本 t 检验
        
        Returns:
            ABTestResult 测试结果
        """
        if len(variant_a_scores) < 2 or len(variant_b_scores) < 2:
            raise ValueError("Sample size too small for T-test")
        
        # 计算均值
        mean_a = np.mean(variant_a_scores)
        mean_b = np.mean(variant_b_scores)
        
        n_a = len(variant_a_scores)
        n_b = len(variant_b_scores)
        
        # 执行 t 检验
        if paired:
            # 配对样本 t 检验
            if n_a != n_b:
                raise ValueError("Paired test requires equal sample sizes")
            t_stat, p_value = stats.ttest_rel(variant_a_scores, variant_b_scores)
        else:
            # 独立样本 t 检验（Welch's t-test，不假设等方差）
            t_stat, p_value = stats.ttest_ind(
                variant_a_scores, 
                variant_b_scores, 
                equal_var=False  # Welch's correction
            )
        
        # 判断显著性
        significant = p_value < self.significance_level
        
        # 计算效应量 (Cohen's d)
        var_a = np.var(variant_a_scores, ddof=1)
        var_b = np.var(variant_b_scores, ddof=1)
        pooled_std = np.sqrt((var_a + var_b) / 2)
        effect_size = (mean_b - mean_a) / pooled_std if pooled_std > 0 else 0
        
        # 做出决策
        decision = self._make_decision(mean_a, mean_b, significant, effect_size)
        
        return ABTestResult(
            test_id=f"t_test_{id(variant_a_scores)}",
            variant_a_mean=float(mean_a),
            variant_b_mean=float(mean_b),
            p_value=float(p_value),
            test_statistic=float(t_stat),
            significant=significant,
            decision=decision,
            confidence_level=self.confidence_level,
            sample_size_a=n_a,
            sample_size_b=n_b,
            effect_size=float(effect_size)
        )
    
    def _make_decision(
        self, 
        mean_a: float, 
        mean_b: float, 
        significant: bool,
        effect_size: float
    ) -> Decision:
        """
        基于统计结果做出决策
        
        Args:
            mean_a: A 组均值
            mean_b: B 组均值
            significant: 是否显著
            effect_size: 效应量
        
        Returns:
            Decision 决策结果
        """
        if not significant:
            # 无显著差异，保留当前版本
            return Decision.KEEP
        
        # 有显著差异
        improvement = (mean_b - mean_a) / mean_a if mean_a != 0 else 0
        
        if improvement > 0.05 and effect_size > 0.2:
            # 显著提升（>5% 且效应量中等以上）
            return Decision.KEEP_AND_PROMOTE
        elif improvement < -0.05:
            # 显著下降（>5%）
            return Decision.ROLLBACK
        else:
            # 虽有显著差异但幅度小，保留
            return Decision.KEEP
    
    def calculate_sample_size(
        self,
        min_detectable_effect: float = 0.1,
        power: float = 0.8,
        variance: float = 1.0,
    ) -> int:
        """
        计算所需的最小样本量
        
        Args:
            min_detectable_effect: 最小可检测效应
            power: 统计功效 (1 - beta)，默认 0.8
            variance: 预期方差
        
        Returns:
            每组所需的最小样本量
        """
        # Z_alpha/2 for two-tailed test
        z_alpha = stats.norm.ppf(1 - self.significance_level / 2)
        # Z_beta for desired power
        z_beta = stats.norm.ppf(power)
        
        # Sample size formula
        n = 2 * variance * (z_alpha + z_beta) ** 2 / (min_detectable_effect ** 2)
        
        return int(np.ceil(n))
    
    def interpret_result(self, result: ABTestResult) -> str:
        """
        生成人类可读的结果解释
        
        Args:
            result: A/B 测试结果
        
        Returns:
            解释文本
        """
        interpretation = f"""
A/B Test Results ({result.test_id}):
{'='*60}
Variant A Mean: {result.variant_a_mean:.4f} (n={result.sample_size_a})
Variant B Mean: {result.variant_b_mean:.4f} (n={result.sample_size_b})

Test Statistic: {result.test_statistic:.4f}
P-value: {result.p_value:.6f}
Significant: {'Yes' if result.significant else 'No'} (α={self.significance_level})
Effect Size (Cohen's d): {result.effect_size:.4f}

Decision: {result.decision.value}

Interpretation:
"""
        
        if result.decision == Decision.KEEP_AND_PROMOTE:
            improvement = ((result.variant_b_mean - result.variant_a_mean) / 
                          result.variant_a_mean * 100)
            interpretation += f"""
✅ Variant B shows statistically significant improvement!
   - Improvement: {improvement:.2f}%
   - Effect size: {abs(result.effect_size):.2f} ({self._interpret_effect_size(result.effect_size)})
   - Recommendation: Promote Variant B to production
"""
        elif result.decision == Decision.ROLLBACK:
            decline = ((result.variant_a_mean - result.variant_b_mean) / 
                      result.variant_a_mean * 100)
            interpretation += f"""
❌ Variant B shows statistically significant decline!
   - Decline: {decline:.2f}%
   - Effect size: {abs(result.effect_size):.2f} ({self._interpret_effect_size(result.effect_size)})
   - Recommendation: Rollback to Variant A
"""
        else:
            interpretation += f"""
⚠️  No statistically significant difference detected.
   - Difference: {abs(result.variant_b_mean - result.variant_a_mean):.4f}
   - Effect size: {abs(result.effect_size):.2f} ({self._interpret_effect_size(result.effect_size)})
   - Recommendation: Keep current version, collect more data if needed
"""
        
        return interpretation
    
    def _interpret_effect_size(self, effect_size: float) -> str:
        """解释效应量大小"""
        abs_effect = abs(effect_size)
        if abs_effect < 0.2:
            return "negligible"
        elif abs_effect < 0.5:
            return "small"
        elif abs_effect < 0.8:
            return "medium"
        else:
            return "large"


# 便捷函数
def ab_test(
    variant_a: List[float],
    variant_b: List[float],
    test_type: TestType = TestType.T_TEST,
    **kwargs
) -> ABTestResult:
    """
    便捷的 A/B 测试函数
    
    Args:
        variant_a: A 组数据
        variant_b: B 组数据
        test_type: 检验类型
        **kwargs: 其他参数
    
    Returns:
        ABTestResult
    """
    framework = ABTestFramework()
    
    if test_type == TestType.Z_TEST:
        return framework.run_z_test(variant_a, variant_b, **kwargs)
    else:
        return framework.run_t_test(variant_a, variant_b, **kwargs)
