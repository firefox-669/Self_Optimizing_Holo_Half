"""
基准对比 HTML 组件生成器

生成可嵌入到主报告中的行业基准对比部分
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from typing import Dict, Any
from benchmarks import generate_benchmark_report


def generate_benchmark_comparison_html(agent_metrics: Dict[str, float], 
                                      task_type: str = "general") -> str:
    """
    生成基准对比的 HTML 片段
    
    Args:
        agent_metrics: Agent 的实际指标
        task_type: 任务类型
    
    Returns:
        HTML 字符串
    """
    benchmark_report = generate_benchmark_report(agent_metrics, task_type)
    comparisons = benchmark_report["comparisons"]
    
    dimension_names = {
        "success_rate": "成功率",
        "efficiency_gain": "效率提升",
        "user_satisfaction": "用户满意度",
        "usage_activity": "使用活跃度",
        "cost_efficiency": "成本效率",
        "innovation": "创新性"
    }
    
    level_colors = {
        "excellent": "#10b981",
        "good": "#3b82f6",
        "average": "#f59e0b",
        "poor": "#ef4444"
    }
    
    level_emojis = {
        "excellent": "🌟",
        "good": "✅",
        "average": "⚠️",
        "poor": "❌"
    }
    
    html = f"""
    <div style="margin-top: 40px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
        <h2 style="margin-top: 0; font-size: 28px; text-align: center;">📊 行业基准对比</h2>
        <p style="text-align: center; opacity: 0.9; margin-bottom: 30px;">
            基于 {benchmark_report['sample_size']} 个任务的行业标准（{benchmark_report['task_type']}）
        </p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
    """
    
    for metric, comparison in comparisons.items():
        cn_name = dimension_names.get(metric, metric)
        actual_value = comparison['actual_value']
        industry_avg = comparison['industry_average']
        gap = comparison['gap_from_average']
        level = comparison['performance_level']
        percentile = comparison['percentile_ranking']
        
        color = level_colors.get(level, "#9ca3af")
        emoji = level_emojis.get(level, "❓")
        progress_pct = min(100, actual_value) if actual_value <= 100 else 50
        
        html += f"""
            <div style="background: rgba(255, 255, 255, 0.15); padding: 20px; border-radius: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; font-size: 18px;">{emoji} {cn_name}</h3>
                    <span style="background: {color}; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                        {level.upper()}
                    </span>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px;">
                        <span>实际值</span>
                        <span style="font-weight: bold;">{actual_value:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; opacity: 0.8;">
                        <span>行业平均</span>
                        <span>{industry_avg:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 14px;">
                        <span>差距</span>
                        <span style="font-weight: bold; color: {'#10b981' if gap >= 0 else '#ef4444'};">
                            {gap:+.2f}
                        </span>
                    </div>
                </div>
                
                <div style="background: rgba(255, 255, 255, 0.2); height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 10px;">
                    <div style="width: {progress_pct}%; height: 100%; background: {color};"></div>
                </div>
                
                <div style="text-align: right; font-size: 12px; opacity: 0.9;">
                    百分位排名: 前 {100-percentile:.0f}%
                </div>
            </div>
        """
    
    excellent_count = sum(1 for c in comparisons.values() if c["performance_level"] == "excellent")
    good_count = sum(1 for c in comparisons.values() if c["performance_level"] == "good")
    total = len(comparisons)
    
    if excellent_count >= 4:
        overall_rating, rating_desc, rating_color = "🌟 卓越", "Agent表现超越90%的同行", "#10b981"
    elif excellent_count + good_count >= 4:
        overall_rating, rating_desc, rating_color = "✅ 优秀", "Agent表现位于前30%", "#3b82f6"
    elif good_count >= 3:
        overall_rating, rating_desc, rating_color = "⚠️ 良好", "Agent表现达到平均水平", "#f59e0b"
    else:
        overall_rating, rating_desc, rating_color = "❌ 需改进", "Agent表现低于平均水平", "#ef4444"
    
    html += f"""
        </div>
        
        <div style="margin-top: 30px; padding: 25px; background: rgba(255, 255, 255, 0.2); border-radius: 10px; text-align: center;">
            <h3 style="margin: 0 0 10px 0; font-size: 24px;">{overall_rating}</h3>
            <p style="margin: 0; font-size: 16px; opacity: 0.9;">{rating_desc}</p>
            <div style="margin-top: 15px; display: flex; justify-content: center; gap: 30px; font-size: 14px;">
                <div><strong>{excellent_count}</strong> 个优秀维度</div>
                <div><strong>{good_count}</strong> 个良好维度</div>
                <div><strong>{total}</strong> 个总维度</div>
            </div>
        </div>
        
        <p style="text-align: center; margin-top: 20px; font-size: 12px; opacity: 0.7;">
            💡 提示: 这些基准会随技术发展更新，建议定期同步最新版本
        </p>
    </div>
    """
    
    return html


if __name__ == "__main__":
    agent_metrics = {
        "success_rate": 82.5,
        "efficiency_gain": 22.0,
        "user_satisfaction": 88.0,
        "usage_activity": 75.0,
        "cost_efficiency": 68.0,
        "innovation": 85.0
    }
    
    print("生成基准对比 HTML...")
    html = generate_benchmark_comparison_html(agent_metrics, "code_generation")
    
    with open("reports/benchmark_comparison_demo.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("✅ 已保存到 reports/benchmark_comparison_demo.html")
