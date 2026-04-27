"""
生成带基准对比的增强版评估报告

展示如何将行业基准数据集成到评估报告中
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from benchmarks import generate_benchmark_report, evaluate_performance_level
from sohh_standard_interface import SOHHDataCollector


def demo_enhanced_report():
    """演示生成带基准对比的报告"""
    
    print("="*70)
    print("📊 增强版评估报告（含行业基准对比）")
    print("="*70)
    
    # 1. 模拟Agent指标
    agent_metrics = {
        "success_rate": 82.5,
        "efficiency_gain": 22.0,
        "user_satisfaction": 88.0,
        "usage_activity": 75.0,
        "cost_efficiency": 68.0,
        "innovation": 85.0
    }
    
    # 2. 生成基准对比报告
    print("\n🔍 正在生成基准对比...")
    benchmark_report = generate_benchmark_report(
        agent_metrics=agent_metrics,
        task_type="code_generation"
    )
    
    print(f"\n✅ 基准对比完成！")
    print(f"   任务类型: {benchmark_report['task_type']}")
    print(f"   样本量: {benchmark_report['sample_size']}")
    
    # 3. 展示对比结果
    print("\n" + "="*70)
    print("📈 六维能力基准对比")
    print("="*70)
    
    dimension_names = {
        "success_rate": "成功率",
        "efficiency_gain": "效率提升",
        "user_satisfaction": "用户满意度",
        "usage_activity": "使用活跃度",
        "cost_efficiency": "成本效率",
        "innovation": "创新性"
    }
    
    for metric, comparison in benchmark_report["comparisons"].items():
        level_emoji = {
            "excellent": "🌟",
            "good": "✅",
            "average": "⚠️",
            "poor": "❌"
        }.get(comparison["performance_level"], "❓")
        
        cn_name = dimension_names.get(metric, metric)
        
        print(f"\n{level_emoji} {cn_name} ({metric}):")
        print(f"   实际值: {comparison['actual_value']:.2f}")
        print(f"   行业平均: {comparison['industry_average']:.2f}")
        print(f"   差距: {comparison['gap_from_average']:+.2f}")
        print(f"   表现等级: {comparison['performance_level']}")
        print(f"   百分位排名: 前 {100-comparison['percentile_ranking']:.0f}%")
    
    # 4. 综合评估
    print("\n" + "="*70)
    print("🎯 综合评估")
    print("="*70)
    
    excellent_count = sum(1 for c in benchmark_report["comparisons"].values() 
                         if c["performance_level"] == "excellent")
    good_count = sum(1 for c in benchmark_report["comparisons"].values() 
                    if c["performance_level"] == "good")
    
    total_dimensions = len(benchmark_report["comparisons"])
    
    print(f"\n优秀维度: {excellent_count}/{total_dimensions}")
    print(f"良好维度: {good_count}/{total_dimensions}")
    
    if excellent_count >= 4:
        overall_rating = "🌟 卓越 - Agent表现超越90%的同行"
    elif excellent_count + good_count >= 4:
        overall_rating = "✅ 优秀 - Agent表现位于前30%"
    elif good_count >= 3:
        overall_rating = "⚠️  良好 - Agent表现达到平均水平"
    else:
        overall_rating = "❌ 需改进 - Agent表现低于平均水平"
    
    print(f"\n总体评级: {overall_rating}")
    
    # 5. 改进建议
    print("\n" + "="*70)
    print("💡 改进建议")
    print("="*70)
    
    poor_metrics = [m for m, c in benchmark_report["comparisons"].items() 
                   if c["performance_level"] in ["average", "poor"]]
    
    if poor_metrics:
        print("\n以下维度需要重点关注:")
        for metric in poor_metrics:
            comparison = benchmark_report["comparisons"][metric]
            cn_name = dimension_names.get(metric, metric)
            gap = comparison["gap_from_average"]
            print(f"   • {cn_name}: 距离行业平均还有 {abs(gap):.2f} 的差距")
    else:
        print("\n🎉 所有维度都达到良好以上水平！继续保持！")
    
    print("\n" + "="*70)
    print("💡 提示: 这些基准会随技术发展更新，建议定期同步最新版本")
    print("="*70)
    
    return benchmark_report


if __name__ == "__main__":
    demo_enhanced_report()
