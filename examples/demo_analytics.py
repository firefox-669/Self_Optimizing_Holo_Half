"""
数据分析引擎使用示例

展示如何使用 DataAnalyticsEngine 进行客观的数据分析。
不涉及 AI 建议，仅基于统计学和规则。
"""

from data_analytics_engine import DataAnalyticsEngine
from datetime import datetime, timedelta
import random


def demo_analytics():
    """演示数据分析功能"""
    
    print("="*70)
    print("📊 SOHH 数据分析引擎演示")
    print("="*70)
    print()
    
    # 1. 创建分析引擎
    print("[1/4] 创建数据分析引擎...")
    engine = DataAnalyticsEngine()
    print("✅ 引擎创建成功")
    print()
    
    # 2. 准备性能数据
    print("[2/4] 准备性能数据...")
    performance_data = {
        'success_rate': 75.75,
        'efficiency_gain': 72.33,
        'user_satisfaction': 82.72,
        'usage_activity': 79.58,
        'cost_efficiency': 65.50,
        'innovation': 69.76,
        'overall_score': 77.16
    }
    print(f"   综合评分: {performance_data['overall_score']}")
    print()
    
    # 3. 生成历史数据（模拟）
    print("[3/4] 生成历史趋势数据...")
    historical_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        # 模拟上升趋势
        progress = i / 30.0
        record = {
            'date': date.isoformat(),
            'success_rate': 70 + progress * 10 + random.uniform(-3, 3),
            'efficiency_gain': 65 + progress * 12 + random.uniform(-4, 4),
            'overall_score': 65 + progress * 18 + random.uniform(-3, 3)
        }
        historical_data.append(record)
    
    print(f"   生成 {len(historical_data)} 天的历史数据")
    print()
    
    # 4. 执行分析
    print("[4/4] 执行数据分析...")
    report = engine.analyze(
        agent_id="openhands-v1.0",
        performance_data=performance_data,
        historical_data=historical_data,
        analysis_period_days=30
    )
    print("✅ 分析完成")
    print()
    
    # 5. 展示分析结果
    print("="*70)
    print("📈 分析报告")
    print("="*70)
    print()
    
    # 核心指标
    print("📊 核心指标:")
    for metric, value in report.metrics_summary.items():
        print(f"   {metric}: {value}")
    print()
    
    # 洞察
    print("💡 关键洞察:")
    for insight in report.insights:
        severity_icon = {
            'info': 'ℹ️ ',
            'warning': '⚠️ ',
            'critical': '🔴'
        }.get(insight.severity, '•')
        
        print(f"   {severity_icon} {insight.title}")
        print(f"      {insight.description}")
        print()
    
    # 趋势
    if report.trends:
        print("📈 趋势分析:")
        for metric, trend in report.trends.items():
            trend_icon = {
                'improving': '📈',
                'declining': '📉',
                'stable': '➡️'
            }.get(trend, '•')
            
            print(f"   {trend_icon} {metric}: {trend}")
        print()
    
    # 基准对比
    print("🎯 行业基准对比:")
    for metric, comparison in report.benchmarks.items():
        level_labels = {
            'excellent': '⭐⭐⭐⭐⭐ 优秀',
            'good': '⭐⭐⭐⭐ 良好',
            'average': '⭐⭐⭐ 平均',
            'below_average': '⭐⭐ 待改进'
        }
        
        current = comparison['current']
        level = comparison['level']
        gap = comparison['gap_to_good']
        
        print(f"   {metric}:")
        print(f"      当前: {current} | 评级: {level_labels.get(level, level)}")
        if gap > 0:
            print(f"      距离'良好'还差: {gap} 分")
        print()
    
    # 6. 导出报告
    print("="*70)
    print("💾 导出报告...")
    filepath = engine.export_analysis(report, "analysis_report_demo.json")
    print(f"✅ 报告已导出: {filepath}")
    print()
    
    print("="*70)
    print("✅ 演示完成！")
    print("="*70)
    print()
    print("📝 总结:")
    print("   - 数据分析引擎提供客观的统计洞察")
    print("   - 不涉及 AI 建议，保持中立性")
    print("   - 可作为标准接口的增值层")
    print("   - 用户可以自由选择是否使用")


if __name__ == "__main__":
    demo_analytics()
