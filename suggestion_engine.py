"""
SOHH 智能建议引擎 (Suggestion Engine)

该模块实现了标准化的进化建议输出协议 (SESP)。
它分析 Agent 的性能数据，识别薄弱环节，并结合行业趋势生成结构化的优化建议。

设计理念：
- 非侵入式：只输出建议，不直接修改项目代码
- 标准化：所有建议都遵循 StandardActionItem 格式
- 可验证：每个建议都包含预期收益指标
"""

from sohh_standard_interface import (
    SuggestionProvider, 
    StandardEvolutionReport, 
    StandardActionItem, 
    SuggestionCategory, 
    PriorityLevel
)
from data_analytics_engine import DataAnalyticsEngine
import sqlite3
from datetime import datetime
from typing import Dict, List
import uuid


class SOHHSuggestionEngine(SuggestionProvider):
    """
    SOHH 标准建议引擎实现
    
    通过接入此引擎，任何项目都可以获取针对其当前表现的、基于数据的进化建议。
    """
    
    def __init__(self, db_path: str = "data/holo_half.db"):
        self.db_path = db_path
        self.analytics = DataAnalyticsEngine()
        # 未来可以在此处集成 ai_news_monitor 或 arXiv API
        self.trend_monitor = SimpleTrendMonitor()

    def get_evolution_suggestions(self, agent_id: str, context: Dict = None) -> StandardEvolutionReport:
        """
        获取针对特定 Agent 的进化建议
        """
        # 1. 获取最新的能力快照作为健康度参考
        latest_snapshot = self._get_latest_snapshot(agent_id)
        health_score = latest_snapshot['overall_score'] if latest_snapshot else 0.0
        
        # 2. 运行深度数据分析以识别瓶颈
        bottlenecks = self._identify_bottlenecks(agent_id)
        
        # 3. 获取相关的行业技术趋势
        trends = self.trend_monitor.get_relevant_trends(bottlenecks)
        
        # 4. 生成标准化的行动项
        action_items = []
        for bottleneck in bottlenecks:
            item = self._create_standard_action(bottleneck, trends)
            action_items.append(item)
            
        # 5. 组装并返回标准报告
        report = StandardEvolutionReport(
            report_id=f"evo_{agent_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            agent_id=agent_id,
            generated_at=datetime.now(),
            current_health_score=health_score,
            action_items=action_items,
            trend_references=trends
        )
        
        return report

    def _get_latest_snapshot(self, agent_id: str) -> Dict:
        """从数据库获取最新的综合能力快照"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM capability_snapshots 
                WHERE agent_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            """, (agent_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                columns = ['snapshot_id', 'agent_id', 'timestamp', 'success_rate', 
                          'efficiency_gain', 'user_satisfaction', 'usage_activity',
                          'cost_efficiency', 'innovation', 'overall_score']
                return dict(zip(columns, row))
        except Exception as e:
            print(f"⚠️ 获取快照失败: {e}")
        return {}

    def _identify_bottlenecks(self, agent_id: str) -> List[Dict]:
        """
        识别性能瓶颈
        返回一个列表，包含得分低于 80 分的维度
        """
        snapshot = self._get_latest_snapshot(agent_id)
        if not snapshot:
            return []
            
        bottlenecks = []
        dimensions = {
            'success_rate': ('成功率', snapshot.get('success_rate', 0)),
            'efficiency_gain': ('效率提升', snapshot.get('efficiency_gain', 0)),
            'user_satisfaction': ('用户满意度', snapshot.get('user_satisfaction', 0)),
            'usage_activity': ('使用活跃度', snapshot.get('usage_activity', 0)),
            'cost_efficiency': ('成本效率', snapshot.get('cost_efficiency', 0)),
            'innovation': ('创新性', snapshot.get('innovation', 0))
        }
        
        for key, (name, score) in dimensions.items():
            if score < 80:
                bottlenecks.append({
                    'metric_key': key,
                    'metric_name': name,
                    'current_score': score,
                    'severity': 'critical' if score < 60 else 'warning'
                })
                
        return sorted(bottlenecks, key=lambda x: x['current_score'])

    def _create_standard_action(self, bottleneck: Dict, trends: List[Dict]) -> StandardActionItem:
        """将诊断结果转化为标准化的行动项"""
        metric_key = bottleneck['metric_key']
        priority = PriorityLevel.CRITICAL if bottleneck['severity'] == 'critical' else PriorityLevel.HIGH
        
        # 根据瓶颈类型生成不同的建议
        if metric_key == 'success_rate':
            return StandardActionItem(
                category=SuggestionCategory.SKILL_UPDATE,
                priority=priority,
                title="增强核心技能的鲁棒性",
                description=f"检测到{bottleneck['metric_name']}仅为 {bottleneck['current_score']:.1f}%。建议在任务执行逻辑中增加错误重试机制和边界条件处理。",
                payload={
                    "target_skill": "core_execution",
                    "modification_type": "add_retry_logic",
                    "max_retries": 3
                },
                expected_metrics={"success_rate": 10.0}
            )
        
        elif metric_key == 'cost_efficiency':
            return StandardActionItem(
                category=SuggestionCategory.PARAMETER_TUNING,
                priority=priority,
                title="优化模型参数以降低 Token 消耗",
                description=f"{bottleneck['metric_name']}较低 ({bottleneck['current_score']:.1f}%)。尝试降低 Temperature 或启用上下文缓存。",
                payload={
                    "param_name": "temperature",
                    "suggested_value": 0.2,
                    "enable_caching": True
                },
                expected_metrics={"cost_per_task": -15.0}
            )
            
        elif metric_key == 'innovation':
            related_trend = next((t for t in trends if 'skill' in t.get('tag', '')), None)
            return StandardActionItem(
                category=SuggestionCategory.TOOL_INTEGRATION,
                priority=PriorityLevel.MEDIUM,
                title="引入前沿技术栈以提升创新能力",
                description=f"当前创新性得分为 {bottleneck['current_score']:.1f}%。{related_trend['description'] if related_trend else '建议探索新的工具集成。'}",
                payload={
                    "integration_target": "advanced_rag",
                    "reference_doc": "https://arxiv.org/abs/latest"
                },
                expected_metrics={"innovation": 15.0}
            )
            
        # 默认建议
        return StandardActionItem(
            category=SuggestionCategory.WORKFLOW_OPTIMIZATION,
            priority=priority,
            title=f"优化 {bottleneck['metric_name']} 工作流",
            description=f"针对 {bottleneck['metric_name']} 偏低的情况，建议审查当前的任务分解策略。",
            payload={"review_step": "task_decomposition"},
            expected_metrics={metric_key: 10.0}
        )


class SimpleTrendMonitor:
    """
    简易趋势监控器
    目前提供静态的行业最佳实践，未来可扩展为实时资讯抓取
    """
    
    def get_relevant_trends(self, bottlenecks: List[Dict]) -> List[Dict[str, str]]:
        trends = [
            {
                "tag": "skill_optimization",
                "title": "Retrieval-Augmented Generation (RAG) 优化",
                "description": "最新的 RAG 技术能显著提升复杂任务的上下文理解能力。",
                "source": "AI Research Weekly"
            },
            {
                "tag": "multi_agent",
                "title": "Multi-Agent Collaboration Patterns",
                "description": "采用多智能体协作模式可将复杂任务的成功率提升至 85% 以上。",
                "source": "AgentBench 2026 Report"
            }
        ]
        return trends


if __name__ == "__main__":
    # 演示用法
    engine = SOHHSuggestionEngine()
    report = engine.get_evolution_suggestions("openhands-v1.0")
    
    print(f"\n📊 SOHH 进化建议报告 (Agent: {report.agent_id})")
    print(f"💯 当前健康度: {report.current_health_score:.2f}")
    print(f"💡 发现 {len(report.action_items)} 个优化机会:\n")
    
    for i, item in enumerate(report.action_items, 1):
        print(f"{i}. [{item.priority.value.upper()}] {item.title}")
        print(f"   📝 {item.description}")
        print(f"   🎯 预期收益: {item.expected_metrics}")
        print("-" * 40)
    
    print("\n🔗 原始 JSON 报告:")
    print(report.to_json())
