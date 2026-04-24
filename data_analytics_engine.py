"""
SOHH 数据分析引擎 v1.0

基于采集的数据提供客观的分析和洞察。
不涉及 AI 建议，仅基于统计学和规则进行分析。

设计理念：
- 客观：基于数据，不主观判断
- 透明：所有分析逻辑公开
- 可选：用户可以只看原始数据
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import statistics


@dataclass
class PerformanceInsight:
    """性能洞察"""
    insight_id: str
    title: str
    description: str
    metric_name: str
    current_value: float
    benchmark_value: float
    trend: str  # "improving", "declining", "stable"
    severity: str  # "info", "warning", "critical"
    
    def to_dict(self) -> Dict:
        return {
            'insight_id': self.insight_id,
            'title': self.title,
            'description': self.description,
            'metric_name': self.metric_name,
            'current_value': self.current_value,
            'benchmark_value': self.benchmark_value,
            'trend': self.trend,
            'severity': self.severity
        }


@dataclass
class AnalysisReport:
    """分析报告"""
    report_id: str
    agent_id: str
    generated_at: datetime
    analysis_period_days: int
    
    # 核心指标
    metrics_summary: Dict[str, float]
    
    # 洞察列表
    insights: List[PerformanceInsight] = field(default_factory=list)
    
    # 趋势分析
    trends: Dict[str, str] = field(default_factory=dict)
    
    # 基准对比
    benchmarks: Dict[str, Dict] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'report_id': self.report_id,
            'agent_id': self.agent_id,
            'generated_at': self.generated_at.isoformat(),
            'analysis_period_days': self.analysis_period_days,
            'metrics_summary': self.metrics_summary,
            'insights': [i.to_dict() for i in self.insights],
            'trends': self.trends,
            'benchmarks': self.benchmarks
        }


class DataAnalyticsEngine:
    """
    数据分析引擎
    
    提供基于数据的客观分析，不涉及 AI 建议。
    
    使用示例：
        engine = DataAnalyticsEngine()
        report = engine.analyze(
            agent_id="openhands-v1.0",
            performance_data={...},
            historical_data=[...]
        )
    """
    
    def __init__(self):
        # 行业基准数据（来自公开研究和基准测试）
        self.benchmarks = {
            'success_rate': {'average': 75.0, 'good': 85.0, 'excellent': 95.0},
            'efficiency_gain': {'average': 60.0, 'good': 75.0, 'excellent': 90.0},
            'user_satisfaction': {'average': 70.0, 'good': 80.0, 'excellent': 90.0},
            'cost_efficiency': {'average': 65.0, 'good': 75.0, 'excellent': 85.0},
            'innovation': {'average': 60.0, 'good': 70.0, 'excellent': 80.0}
        }
    
    def analyze(self, agent_id: str, 
                performance_data: Dict,
                historical_data: List[Dict] = None,
                analysis_period_days: int = 30) -> AnalysisReport:
        """
        执行数据分析
        
        Args:
            agent_id: Agent 标识
            performance_data: 当前性能数据
            historical_data: 历史数据（用于趋势分析）
            analysis_period_days: 分析周期
            
        Returns:
            AnalysisReport
        """
        report = AnalysisReport(
            report_id=f"analysis_{datetime.now().timestamp()}",
            agent_id=agent_id,
            generated_at=datetime.now(),
            analysis_period_days=analysis_period_days,
            metrics_summary=performance_data.copy()
        )
        
        # 1. 生成洞察
        report.insights = self._generate_insights(performance_data)
        
        # 2. 趋势分析
        if historical_data:
            report.trends = self._analyze_trends(historical_data)
        
        # 3. 基准对比
        report.benchmarks = self._compare_with_benchmarks(performance_data)
        
        return report
    
    def _generate_insights(self, data: Dict) -> List[PerformanceInsight]:
        """基于规则生成洞察"""
        insights = []
        
        # 成功率洞察
        success_rate = data.get('success_rate', 0)
        if success_rate < 70:
            insights.append(PerformanceInsight(
                insight_id="insight-001",
                title="成功率低于行业平均水平",
                description=f"当前成功率 {success_rate}% 低于行业平均 75%",
                metric_name="success_rate",
                current_value=success_rate,
                benchmark_value=75.0,
                trend="needs_improvement",
                severity="warning"
            ))
        elif success_rate > 90:
            insights.append(PerformanceInsight(
                insight_id="insight-002",
                title="成功率表现优秀",
                description=f"当前成功率 {success_rate}% 超过行业优秀水平 90%",
                metric_name="success_rate",
                current_value=success_rate,
                benchmark_value=90.0,
                trend="excellent",
                severity="info"
            ))
        
        # 效率洞察
        efficiency = data.get('efficiency_gain', 0)
        if efficiency < 60:
            insights.append(PerformanceInsight(
                insight_id="insight-003",
                title="效率有较大提升空间",
                description=f"当前效率评分 {efficiency}% 低于行业平均 60%",
                metric_name="efficiency_gain",
                current_value=efficiency,
                benchmark_value=60.0,
                trend="needs_improvement",
                severity="warning"
            ))
        
        # 成本效率洞察
        cost_eff = data.get('cost_efficiency', 0)
        if cost_eff < 65:
            insights.append(PerformanceInsight(
                insight_id="insight-004",
                title="成本控制需要优化",
                description=f"当前成本效率 {cost_eff}% 低于行业平均 65%",
                metric_name="cost_efficiency",
                current_value=cost_eff,
                benchmark_value=65.0,
                trend="needs_improvement",
                severity="warning"
            ))
        
        # 综合健康度
        overall = data.get('overall_score', 0)
        if overall < 70:
            insights.append(PerformanceInsight(
                insight_id="insight-005",
                title="整体性能需要关注",
                description=f"综合评分 {overall} 分，建议重点关注薄弱环节",
                metric_name="overall_score",
                current_value=overall,
                benchmark_value=75.0,
                trend="needs_attention",
                severity="warning"
            ))
        
        return insights
    
    def _analyze_trends(self, historical_data: List[Dict]) -> Dict[str, str]:
        """分析历史趋势"""
        if len(historical_data) < 3:
            return {}
        
        trends = {}
        
        # 分析每个指标的趋势
        for metric in ['success_rate', 'efficiency_gain', 'overall_score']:
            values = [d.get(metric, 0) for d in historical_data if metric in d]
            
            if len(values) >= 3:
                # 计算斜率
                recent_avg = statistics.mean(values[-3:])
                earlier_avg = statistics.mean(values[:3])
                
                change_rate = (recent_avg - earlier_avg) / earlier_avg if earlier_avg > 0 else 0
                
                if change_rate > 0.05:
                    trends[metric] = "improving"
                elif change_rate < -0.05:
                    trends[metric] = "declining"
                else:
                    trends[metric] = "stable"
        
        return trends
    
    def _compare_with_benchmarks(self, data: Dict) -> Dict[str, Dict]:
        """与行业基准对比"""
        comparison = {}
        
        for metric, benchmark in self.benchmarks.items():
            current_value = data.get(metric, 0)
            
            if current_value >= benchmark['excellent']:
                level = "excellent"
            elif current_value >= benchmark['good']:
                level = "good"
            elif current_value >= benchmark['average']:
                level = "average"
            else:
                level = "below_average"
            
            comparison[metric] = {
                'current': current_value,
                'benchmark_average': benchmark['average'],
                'benchmark_good': benchmark['good'],
                'benchmark_excellent': benchmark['excellent'],
                'level': level,
                'gap_to_good': round(benchmark['good'] - current_value, 2)
            }
        
        return comparison
    
    def export_analysis(self, report: AnalysisReport, filepath: str) -> str:
        """导出分析报告为 JSON"""
        import json
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        
        return filepath
