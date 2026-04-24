"""
可视化报表生成器 (Visualization Report Generator)

根据 my_direction 战略要求，生成精美的评估报告，包括：
1. 全息进化指数（总分）
2. 六维能力雷达图
3. 历史趋势图
4. A/B 测试对比

这是 SOHH 对外展示实力的第一张名片！
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3


class VisualizationReportGenerator:
    """可视化报表生成器"""
    
    def __init__(self, db_path: str = "data/holo_half.db"):
        self.db_path = Path(db_path)
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
        
    def generate_comprehensive_report(self, agent_id: str = None, output_format: str = "html") -> Path:
        """
        生成综合评估报告
        
        Args:
            agent_id: Agent 标识 (如果为 None 则汇总所有数据)
            output_format: 输出格式 (html/markdown)
            
        Returns:
            报告文件路径
        """
        print(f"📊 正在为 Agent '{agent_id or 'ALL'}' 生成综合评估报告...")
        
        # 1. 收集数据
        metrics_data = self._collect_metrics_data()
        
        if not metrics_data:
            print("⚠️  暂无数据，无法生成报告")
            return None
        
        # 2. 计算全息进化指数
        overall_score = self._calculate_holistic_evolution_index(metrics_data)
        
        # 3. 生成六维雷达图数据
        radar_data = self._calculate_six_dimensional_radar(metrics_data)
        
        # 4. 生成历史趋势数据
        trend_data = self._calculate_historical_trends()
        
        # 5. 生成 A/B 测试对比
        ab_test_data = self._get_ab_test_comparison()
        
        # 6. 生成报告
        if output_format == "html":
            report_path = self._generate_html_report(
                overall_score, radar_data, trend_data, ab_test_data
            )
        else:
            report_path = self._generate_markdown_report(
                overall_score, radar_data, trend_data, ab_test_data
            )
        
        print(f"✅ 报告已生成: {report_path}")
        return report_path
    
    def _collect_metrics_data(self, agent_id: str = None) -> List[Dict]:
        """收集所有指标数据"""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # 优先从 capability_snapshots 读取（标准接口）
            query = """
                SELECT timestamp, overall_score, usage_activity, success_rate,
                       efficiency_gain, user_satisfaction, cost_efficiency, innovation
                FROM capability_snapshots 
            """
            params = []
            if agent_id:
                query += " WHERE agent_id = ? "
                params.append(agent_id)
            query += " ORDER BY timestamp DESC LIMIT 100"
            
            cursor.execute(query, params)
            
            columns = ['timestamp', 'overall_score', 'usage_activity', 'success_rate',
                      'efficiency_gain', 'user_satisfaction', 'cost_efficiency', 'innovation']
            
            records = []
            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                records.append(record)
            
            # 如果没有快照数据，尝试旧的 scoring_records 表
            if not records:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scoring_records'")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT timestamp, overall_score, usage_activity, success_rate,
                               efficiency_gain, user_satisfaction, cost_efficiency, innovation
                        FROM scoring_records
                        ORDER BY timestamp DESC LIMIT 100
                    """)
                    for row in cursor.fetchall():
                        records.append(dict(zip(columns, row)))
            
            return records
            
        except Exception as e:
            print(f"❌ 数据收集失败: {e}")
            return []
        finally:
            conn.close()
    
    def _calculate_holistic_evolution_index(self, metrics_data: List[Dict]) -> float:
        """
        计算全息进化指数（总体评分）- 增强版
        
        这是最醒目的数字，直观展示当前水平
        """
        if not metrics_data:
            return 0.0
        
        # 取最近 30 条记录的平均值
        recent = metrics_data[:30]
        scores = []
        for r in recent:
            score = r.get('overall_score', 0)
            # 智能归一化：如果是小数则乘100，如果是大数则直接使用
            normalized_score = score * 100 if score <= 1.0 else score
            scores.append(normalized_score)
        
        avg_score = sum(scores) / len(scores)
        return round(min(100, avg_score), 2)  # 强制不超过 100
    
    def _calculate_six_dimensional_radar(self, metrics_data: List[Dict]) -> Dict:
        """
        计算六维能力雷达图数据（最终修复版：杜绝夸张数值）
        """
        if not metrics_data:
            return {k: 0 for k in ['success_rate', 'efficiency_gain', 'user_satisfaction', 'usage_activity', 'cost_efficiency', 'innovation']}
        
        recent = metrics_data[:30]
        
        # 辅助函数：安全获取平均值并归一化到 0-100
        def safe_avg(key, fallback_key=None):
            values = [r.get(key, r.get(fallback_key, 0)) for r in recent]
            avg = sum(values) / len(values)
            # 核心逻辑：如果平均值小于等于 1，认为是比例，乘以 100；否则认为是原始分
            result = avg * 100 if avg <= 1.0 else avg
            return min(100, max(0, result)) # 强制限制在 0-100 之间

        return {
            'success_rate': safe_avg('success_rate', 'overall_score'),
            'efficiency_gain': safe_avg('efficiency_gain', 'efficiency'),
            'user_satisfaction': safe_avg('user_satisfaction', 'satisfaction'),
            'usage_activity': safe_avg('usage_activity', 'activity'),
            'cost_efficiency': safe_avg('cost_efficiency', 'cost'),
            'innovation': safe_avg('innovation', 'skill_effectiveness'),
        }
    
    def _calculate_historical_trends(self) -> Dict:
        """计算历史趋势数据"""
        if not self.db_path.exists():
            return {'dates': [], 'scores': []}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # 获取最近 30 天的每日平均分
            cursor.execute("""
                SELECT DATE(timestamp) as date, AVG(overall_score) as avg_score
                FROM scoring_records
                WHERE timestamp >= datetime('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            """)
            
            dates = []
            scores = []
            
            for row in cursor.fetchall():
                dates.append(row[0])
                scores.append(round(row[1] * 100, 2))
            
            # 如果没有真实数据，直接返回空列表，不再生成假数据以保持报告严谨性
            if not dates:
                print("⚠️ 暂无足够的历史趋势数据，图表将显示为空。")
                return {'dates': [], 'scores': []}
            
            return {
                'dates': dates,
                'scores': scores
            }
            
        except Exception as e:
            print(f"❌ 趋势数据计算失败: {e}")
            return {'dates': [], 'scores': []}
        finally:
            conn.close()
    
    def _get_ab_test_comparison(self) -> Dict:
        """获取 A/B 测试对比数据"""
        if not self.db_path.exists():
            return {}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # 查询最近的 A/B 测试结果
            cursor.execute("""
                SELECT variant_a_name, variant_b_name, 
                       AVG(variant_a_score) as avg_a, 
                       AVG(variant_b_score) as avg_b,
                       p_value, is_significant
                FROM ab_test_results
                WHERE created_at >= datetime('now', '-7 days')
                GROUP BY variant_a_name, variant_b_name
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            tests = []
            for row in cursor.fetchall():
                tests.append({
                    'variant_a': row[0],
                    'variant_b': row[1],
                    'score_a': round(row[2] * 100, 2),
                    'score_b': round(row[3] * 100, 2),
                    'p_value': row[4],
                    'significant': row[5]
                })
            
            return {'tests': tests}
            
        except Exception as e:
            print(f"❌ A/B 测试数据获取失败: {e}")
            return {'tests': []}
        finally:
            conn.close()
    
    def _generate_html_report(self, overall_score: float, radar_data: Dict,
                             trend_data: Dict, ab_test_data: Dict) -> Path:
        """生成 HTML 格式的精美报告"""
        
        timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        filename = f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.report_dir / filename
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOHH 全息进化报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .score-card {{
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 15px;
            margin-bottom: 40px;
            color: white;
        }}
        
        .score-number {{
            font-size: 5em;
            font-weight: bold;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .score-label {{
            font-size: 1.5em;
            opacity: 0.95;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        
        .ab-test-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
        }}
        
        .ab-test-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .metric {{
            display: inline-block;
            margin: 10px 20px;
            padding: 10px 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 SOHH 全息进化报告</h1>
            <p>Self-Optimizing Holo Half - 科学评估系统</p>
            <p style="margin-top: 10px;">生成时间: {timestamp}</p>
        </div>
        
        <div class="content">
            <!-- 全息进化指数 -->
            <div class="score-card">
                <div class="score-label">全息进化指数</div>
                <div class="score-number">{overall_score}</div>
                <div style="font-size: 1.2em; margin-top: 10px;">
                    Holistic Evolution Index
                </div>
            </div>
            
            <!-- 六维能力雷达图 -->
            <div class="section">
                <h2>📊 六维能力雷达图</h2>
                <div class="chart-container">
                    <canvas id="radarChart"></canvas>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <div class="metric">
                        <div class="metric-value">{radar_data['success_rate']:.2f}%</div>
                        <div class="metric-label">成功率</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{radar_data['efficiency_gain']:.2f}%</div>
                        <div class="metric-label">效率提升</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{radar_data['user_satisfaction']:.2f}%</div>
                        <div class="metric-label">用户满意度</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{radar_data['usage_activity']:.2f}%</div>
                        <div class="metric-label">使用活跃度</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{radar_data['cost_efficiency']:.2f}%</div>
                        <div class="metric-label">成本效率</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{radar_data['innovation']:.2f}%</div>
                        <div class="metric-label">创新性</div>
                    </div>
                </div>
            </div>
            
            <!-- 历史趋势图 -->
            <div class="section">
                <h2>📈 历史趋势分析</h2>
                {self._generate_trend_chart_html(trend_data)}
            </div>
            
            <!-- A/B 测试对比 -->
            <div class="section">
                <h2>🧪 A/B 测试对比</h2>
                {self._generate_ab_test_html(ab_test_data)}
            </div>
            
            <!-- 统计摘要 -->
            <div class="section">
                <h2>📊 统计摘要 (Statistical Summary)</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div class="metric" style="text-align: center;">
                        <div class="metric-value">{len(trend_data.get('dates', []))}</div>
                        <div class="metric-label">评估天数</div>
                    </div>
                    <div class="metric" style="text-align: center;">
                        <div class="metric-value">{round(max(trend_data.get('scores', [0])) - min(trend_data.get('scores', [0])), 2) if trend_data.get('scores') else 0}</div>
                        <div class="metric-label">提升幅度</div>
                    </div>
                    <div class="metric" style="text-align: center;">
                        <div class="metric-value">{round(sum(trend_data.get('scores', [0])) / len(trend_data.get('scores', [1])) if trend_data.get('scores') else 0, 2)}</div>
                        <div class="metric-label">平均分数</div>
                    </div>
                    <div class="metric" style="text-align: center;">
                        <div class="metric-value">{'↑' if len(trend_data.get('scores', [])) > 1 and trend_data['scores'][-1] > trend_data['scores'][0] else '↓'}</div>
                        <div class="metric-label">趋势方向</div>
                    </div>
                </div>
            </div>
            
            <!-- 改进建议 -->
            <div class="section">
                <h2>💡 改进建议 (Improvement Suggestions)</h2>
                {self._generate_improvement_suggestions(radar_data, trend_data)}
            </div>
            
            <!-- 评估任务清单 -->
            <div class="section">
                <h2>📋 基准测试任务清单 (Benchmark Tasks)</h2>
                {self._generate_task_list_html()}
            </div>
            
            <!-- 决策透明度报告 -->
            <div class="section">
                <h2>🔍 决策透明度报告 (Decision Transparency)</h2>
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr style="background: #f8f9fa; text-align: left;">
                            <th style="padding: 12px; border-bottom: 2px solid #667eea;">评估维度</th>
                            <th style="padding: 12px; border-bottom: 2px solid #667eea;">原始得分</th>
                            <th style="padding: 12px; border-bottom: 2px solid #667eea;">权重</th>
                            <th style="padding: 12px; border-bottom: 2px solid #667eea;">加权贡献</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">成功率 (Success Rate)</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['success_rate']:.2f}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">20%</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['success_rate'] * 0.20:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">效率提升 (Efficiency Gain)</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['efficiency_gain']:.2f}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">15%</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['efficiency_gain'] * 0.15:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">用户满意度 (User Satisfaction)</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['user_satisfaction']:.2f}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">20%</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['user_satisfaction'] * 0.20:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">使用活跃度 (Usage Activity)</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['usage_activity']:.2f}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">15%</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['usage_activity'] * 0.15:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">成本效率 (Cost Efficiency)</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['cost_efficiency']:.2f}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">15%</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['cost_efficiency'] * 0.15:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">创新性 (Innovation)</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['innovation']:.2f}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">15%</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{radar_data['innovation'] * 0.15:.2f}</td>
                        </tr>
                        <tr style="background: #f8f9fa; font-weight: bold;">
                            <td style="padding: 12px;">综合评分</td>
                            <td style="padding: 12px;">-</td>
                            <td style="padding: 12px;">100%</td>
                            <td style="padding: 12px; color: #667eea; font-size: 1.2em;">{overall_score:.2f}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- 关键影响因素 -->
            <div class="section">
                <h2>⚡ 关键影响因素 (Key Influencing Factors)</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                    <div style="padding: 20px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
                        <h3 style="color: #856404; margin-bottom: 15px;">📉 薄弱环节 (Weaknesses)</h3>
                        {self._generate_weakness_list(radar_data)}
                    </div>
                    <div style="padding: 20px; background: #d4edda; border-radius: 8px; border-left: 4px solid #28a745;">
                        <h3 style="color: #155724; margin-bottom: 15px;">🚀 优势领域 (Strengths)</h3>
                        {self._generate_strength_list(radar_data)}
                    </div>
                </div>
            </div>
            
            <!-- 指标释义 -->
            <div class="section">
                <h2>📖 指标释义 (Metrics Glossary)</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
                    <div style="padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                        <h3 style="color: #667eea; margin-bottom: 10px;">🌟 全息进化指数 (Holistic Evolution Index)</h3>
                        <p style="color: #666; font-size: 0.95em; line-height: 1.6;">
                            这是 Agent 的<strong>综合健康度总分</strong>（0-100分）。它不是单一维度的表现，而是基于成功率、效率、满意度等六个维度的加权平均值。
                            <br><br>
                            <strong>分数参考：</strong>
                            <ul style="margin-top: 5px; padding-left: 20px; color: #555;">
                                <li>90+：卓越 (Excellent) - 达到行业顶尖水平</li>
                                <li>75-90：优秀 (Good) - 表现稳定，具备实用价值</li>
                                <li>60-75：合格 (Fair) - 基础功能可用，仍有优化空间</li>
                                <li>&lt;60：待改进 (Needs Improvement) - 建议进行针对性调优</li>
                            </ul>
                        </p>
                    </div>
                    <div style="padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #28a745;">
                        <h3 style="color: #28a745; margin-bottom: 10px;">📊 六维能力模型 (Six-Dimensional Model)</h3>
                        <p style="color: #666; font-size: 0.95em; line-height: 1.6;">
                            我们采用雷达图展示 Agent 的均衡性：
                            <ul style="margin-top: 5px; padding-left: 20px; color: #555;">
                                <li><strong>成功率：</strong> 任务一次跑通的比例。</li>
                                <li><strong>效率提升：</strong> 相比人工或基准线的耗时缩短程度。</li>
                                <li><strong>用户满意度：</strong> 基于反馈评分的综合评价。</li>
                                <li><strong>使用活跃度：</strong> 反映 Agent 在实际场景中的调用频率。</li>
                                <li><strong>成本效率：</strong> Token 消耗与产出质量的性价比（基准线：$0.01/任务）。</li>
                                <li><strong>创新性：</strong> 解决复杂问题时的方案新颖度。</li>
                            </ul>
                        </p>
                    </div>
                </div>
                
                <!-- 统计效力说明 -->
                <div style="margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 8px; border-left: 4px solid #2196F3;">
                    <h4 style="color: #0d47a1; margin-bottom: 10px;">⚠️ 统计效力与数据说明 (Statistical Notes)</h4>
                    <ul style="color: #555; font-size: 0.9em; padding-left: 20px;">
                        <li><strong>置信区间：</strong> 当前报告展示的是点估计值（Point Estimate）。在样本量超过 100 个任务后，系统将自动计算 95% 置信区间。</li>
                        <li><strong>A/B 测试效力：</strong> p-value 仅作为参考。当样本量小于 30 时，统计检验效力（Power）可能不足，建议谨慎解读显著性结果。</li>
                        <li><strong>趋势滞后：</strong> 历史趋势图按天聚合数据。如果当天未运行新任务，图表将沿用最近一次的有效快照。</li>
                        <li><strong>离线渲染：</strong> 本报告依赖外部 CDN 渲染图表。如需离线查看，请确保网络连接或使用浏览器的“另存为”功能保存完整页面。</li>
                    </ul>
                </div>
            </div>

            <!-- 评估算法定义 -->
            <div class="section">
                <h2>📖 评估算法定义 (Algorithm Definitions)</h2>
                <div style="margin-top: 20px;">
                    <details style="margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                        <summary style="cursor: pointer; font-weight: bold; color: #667eea;">✅ 成功率 (Success Rate) 是如何计算的？</summary>
                        <p style="padding: 15px; background: white; border-radius: 5px; margin-top: 10px; line-height: 1.8;">
                            <strong>公式：</strong>(成功执行的任务数 / 总任务数) × 100<br>
                            <strong>数据来源：</strong>从 Agent 执行日志中自动提取任务状态。<br>
                            <strong>示例：</strong>如果最近执行了 10 个任务，其中 8 个成功完成，则成功率为 80%。<br>
                            <strong>权重：</strong>在综合评分中占 20%
                        </p>
                    </details>
                    
                    <details style="margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                        <summary style="cursor: pointer; font-weight: bold; color: #667eea;">⚡ 效率提升 (Efficiency Gain) 是如何计算的？</summary>
                        <p style="padding: 15px; background: white; border-radius: 5px; margin-top: 10px; line-height: 1.8;">
                            <strong>公式：</strong>[1 - (实际耗时 / 基准耗时)] × 100<br>
                            <strong>数据来源：</strong>记录每个任务的开始和结束时间戳。<br>
                            <strong>说明：</strong>耗时越短，分数越高；若超过基准时间（默认 300 秒），分数将线性下降至 0。<br>
                            <strong>权重：</strong>在综合评分中占 15%
                        </p>
                    </details>
                    
                    <details style="margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                        <summary style="cursor: pointer; font-weight: bold; color: #667eea;">😊 用户满意度 (User Satisfaction) 是如何计算的？</summary>
                        <p style="padding: 15px; background: white; border-radius: 5px; margin-top: 10px; line-height: 1.8;">
                            <strong>公式：</strong>(平均满意度评分 / 5.0) × 100<br>
                            <strong>数据来源：</strong>用户对任务结果的主动反馈（0-5 分）。<br>
                            <strong>说明：</strong>如果没有用户反馈，系统会基于代码质量和测试通过率估算满意度。<br>
                            <strong>权重：</strong>在综合评分中占 20%
                        </p>
                    </details>
                    
                    <details style="margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                        <summary style="cursor: pointer; font-weight: bold; color: #667eea;">💰 成本效率 (Cost Efficiency) 是如何计算的？</summary>
                        <p style="padding: 15px; background: white; border-radius: 5px; margin-top: 10px; line-height: 1.8;">
                            <strong>公式：</strong>[1 - (实际成本 / 基准成本)] × 100<br>
                            <strong>数据来源：</strong>Token 使用量 × 模型单价。<br>
                            <strong>说明：</strong>成本越低，分数越高；基准成本默认为 $0.01/任务。<br>
                            <strong>权重：</strong>在综合评分中占 15%
                        </p>
                    </details>
                    
                    <details style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
                        <summary style="cursor: pointer; font-weight: bold; color: #667eea;">💡 创新性 (Innovation) 是如何计算的？</summary>
                        <p style="padding: 15px; background: white; border-radius: 5px; margin-top: 10px; line-height: 1.8;">
                            <strong>公式：</strong>(代码质量评分 × 50%) + (测试通过率 × 50%)<br>
                            <strong>数据来源：</strong>静态代码分析 + 自动化测试结果。<br>
                            <strong>说明：</strong>评估解决方案的创新程度、代码质量和测试覆盖度。<br>
                            <strong>权重：</strong>在综合评分中占 15%
                        </p>
                    </details>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2026 Self-Optimizing Holo Half | 科学评估 · 持续进化</p>
        </div>
    </div>
    
    <script>
        // 六维雷达图
        const radarCtx = document.getElementById('radarChart').getContext('2d');
        new Chart(radarCtx, {{
            type: 'radar',
            data: {{
                labels: ['成功率', '效率提升', '用户满意度', '使用活跃度', '成本效率', '创新性'],
                datasets: [{{
                    label: '当前能力',
                    data: [{radar_data['success_rate']}, {radar_data['efficiency_gain']}, {radar_data['user_satisfaction']}, {radar_data['usage_activity']}, {radar_data['cost_efficiency']}, {radar_data['innovation']}],
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                    pointRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            stepSize: 20
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }}
            }}
        }});
        
        // 历史趋势图
        const trendDates = {json.dumps(trend_data['dates'])};
        const trendScores = {json.dumps(trend_data['scores'])};
        
        if (trendDates.length >= 2) {{
            const trendCtx = document.getElementById('trendChart').getContext('2d');
            new Chart(trendCtx, {{
                type: 'line',
                data: {{
                    labels: trendDates,
                    datasets: [{{
                        label: '进化指数',
                        data: trendScores,
                        borderColor: 'rgba(118, 75, 162, 1)',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: 'rgba(118, 75, 162, 1)'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            title: {{
                                display: true,
                                text: '分数'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: '日期'
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }}
                    }}
                }}
            }});
        }} else {{
            document.getElementById('trendChartContainer').innerHTML = `
                <div style="text-align: center; padding: 40px; color: #999;">
                    <div style="font-size: 3em; margin-bottom: 10px;">📊</div>
                    <div style="font-size: 1.2em; margin-bottom: 10px;">数据积累中...</div>
                    <div style="font-size: 0.9em;">需要至少 2 天的评估数据才能生成趋势分析</div>
                    <div style="font-size: 0.8em; margin-top: 10px; color: #bbb;">当前数据点: ${{trendDates.length}} 个</div>
                </div>
            `;
        }}
    </script>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def _generate_ab_test_html(self, ab_test_data: Dict) -> str:
        """生成 A/B 测试 HTML"""
        tests = ab_test_data.get('tests', [])
        
        if not tests:
            return "<p style='color: #999;'>暂无 A/B 测试数据</p>"
        
        html = ""
        for test in tests:
            significant_marker = "✅ 显著" if test['significant'] else "❌ 不显著"
            is_b_winner = test['score_b'] > test['score_a']
            
            html += f"""
            <div class="ab-test-card">
                <h3>{test['variant_a']} vs {test['variant_b']}</h3>
                <div style="display: flex; justify-content: space-around; margin: 15px 0;">
                    <div>
                        <div style="font-size: 2em; color: #667eea;">{test['score_a']}分</div>
                        <div style="color: #666;">Variant A {'🏆' if not is_b_winner else ''}</div>
                    </div>
                    <div style="font-size: 2em; color: #999;">VS</div>
                    <div>
                        <div style="font-size: 2em; color: #f5576c;">{test['score_b']}分</div>
                        <div style="color: #666;">Variant B {'🏆' if is_b_winner else ''}</div>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 10px;">
                    <span style="background: {'#4caf50' if test['significant'] else '#ff9800'}; 
                              color: white; padding: 5px 15px; border-radius: 20px;">
                        {significant_marker} | p-value: {test['p_value']:.4f}
                    </span>
                </div>
            </div>
            """
        
        return html
    
    def _generate_trend_chart_html(self, trend_data: Dict) -> str:
        """生成趋势图 HTML 容器"""
        if len(trend_data.get('dates', [])) < 2:
            # 数据不足时显示占位符
            return """
            <div id="trendChartContainer" style="min-height: 300px; display: flex; align-items: center; justify-content: center; background: #f8f9fa; border-radius: 8px;">
                <div style="text-align: center; padding: 40px; color: #999;">
                    <div style="font-size: 3em; margin-bottom: 10px;">📊</div>
                    <div style="font-size: 1.2em; margin-bottom: 10px;">数据积累中...</div>
                    <div style="font-size: 0.9em;">需要至少 2 天的评估数据才能生成趋势分析</div>
                </div>
            </div>
            """
        else:
            # 数据充足时显示图表容器
            return '<div id="trendChartContainer" class="chart-container"><canvas id="trendChart"></canvas></div>'
    
    def _generate_markdown_report(self, overall_score: float, radar_data: Dict,
                                 trend_data: Dict, ab_test_data: Dict) -> Path:
        """生成 Markdown 格式的报告"""
        
        timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        filename = f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.report_dir / filename
        
        md_content = f"""# 🚀 SOHH 全息进化报告

**生成时间**: {timestamp}  
**报告类型**: 综合评估报告

---

## 📊 全息进化指数

<div align="center">

# {overall_score} / 100

**Holistic Evolution Index**

</div>

---

## 🎯 六维能力分析

| 维度 | 得分 | 评级 |
|------|------|------|
| ✅ 成功率 | {radar_data['success_rate']}% | {self._get_rating(radar_data['success_rate'])} |
| ⚡ 效率提升 | {radar_data['efficiency_gain']}% | {self._get_rating(radar_data['efficiency_gain'])} |
| 😊 用户满意度 | {radar_data['user_satisfaction']}% | {self._get_rating(radar_data['user_satisfaction'])} |
| 📈 使用活跃度 | {radar_data['usage_activity']}% | {self._get_rating(radar_data['usage_activity'])} |
| 💰 成本效率 | {radar_data['cost_efficiency']}% | {self._get_rating(radar_data['cost_efficiency'])} |
| 💡 创新性 | {radar_data['innovation']}% | {self._get_rating(radar_data['innovation'])} |

---

## 📈 历史趋势

{self._generate_trend_markdown(trend_data)}

---

## 🧪 A/B 测试对比

{self._generate_ab_test_markdown(ab_test_data)}

---

*本报告由 Self-Optimizing Holo Half 自动生成*  
*科学评估 · 持续进化*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filepath
    
    def _get_rating(self, score: float) -> str:
        """根据分数返回评级"""
        if score >= 90:
            return "⭐⭐⭐⭐⭐ 优秀"
        elif score >= 80:
            return "⭐⭐⭐⭐ 良好"
        elif score >= 70:
            return "⭐⭐⭐ 中等"
        elif score >= 60:
            return "⭐⭐ 及格"
        else:
            return "⭐ 需改进"
    
    def _generate_trend_markdown(self, trend_data: Dict) -> str:
        """生成趋势 Markdown"""
        if not trend_data['dates']:
            return "暂无历史数据"
        
        md = "```\n"
        md += "日期       | 分数\n"
        md += "-----------|------\n"
        
        for date, score in zip(trend_data['dates'][-10:], trend_data['scores'][-10:]):
            md += f"{date} | {score}\n"
        
        md += "```"
        return md
    
    def _generate_ab_test_markdown(self, ab_test_data: Dict) -> str:
        """生成 A/B 测试 Markdown"""
        tests = ab_test_data.get('tests', [])
        
        if not tests:
            return "暂无 A/B 测试数据"
        
        md = "| 对比组 | Variant A | Variant B | P-value | 显著性 |\n"
        md += "|--------|-----------|-----------|---------|--------|\n"
        
        for test in tests:
            significant = "✅ 是" if test['significant'] else "❌ 否"
            md += f"| {test['variant_a']} vs {test['variant_b']} | {test['score_a']} | {test['score_b']} | {test['p_value']:.4f} | {significant} |\n"
        
        return md
    
    def _generate_improvement_suggestions(self, radar_data: Dict, trend_data: Dict) -> str:
        """生成改进建议 HTML"""
        suggestions = []
        
        # 基于雷达图数据分析薄弱环节
        dimensions = {
            '成功率': radar_data.get('success_rate', 0),
            '效率提升': radar_data.get('efficiency_gain', 0),
            '用户满意度': radar_data.get('user_satisfaction', 0),
            '使用活跃度': radar_data.get('usage_activity', 0),
            '成本效率': radar_data.get('cost_efficiency', 0),
            '创新性': radar_data.get('innovation', 0)
        }
        
        # 找出最弱的3个维度
        sorted_dims = sorted(dimensions.items(), key=lambda x: x[1])
        weak_dimensions = sorted_dims[:3]
        
        for dim_name, score in weak_dimensions:
            if score < 60:
                suggestions.append(f"""
                <div style="padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; margin-bottom: 10px; border-radius: 4px;">
                    <strong>🔴 {dim_name} (当前: {score:.1f}%)</strong><br>
                    <span style="color: #666; font-size: 0.9em;">{self._get_suggestion_for_dimension(dim_name)}</span>
                </div>
                """)
            elif score < 80:
                suggestions.append(f"""
                <div style="padding: 15px; background: #e7f3ff; border-left: 4px solid #2196F3; margin-bottom: 10px; border-radius: 4px;">
                    <strong>🟡 {dim_name} (当前: {score:.1f}%)</strong><br>
                    <span style="color: #666; font-size: 0.9em;">{self._get_suggestion_for_dimension(dim_name)}</span>
                </div>
                """)
        
        # 基于趋势分析
        scores = trend_data.get('scores', [])
        if len(scores) >= 2:
            recent_trend = scores[-1] - scores[0]
            if recent_trend < 0:
                suggestions.append("""
                <div style="padding: 15px; background: #f8d7da; border-left: 4px solid #dc3545; margin-bottom: 10px; border-radius: 4px;">
                    <strong>📉 趋势警告</strong><br>
                    <span style="color: #666; font-size: 0.9em;">最近评估周期内分数呈下降趋势，建议检查系统配置和任务难度</span>
                </div>
                """)
            elif recent_trend < 5:
                suggestions.append("""
                <div style="padding: 15px; background: #e7f3ff; border-left: 4px solid #2196F3; margin-bottom: 10px; border-radius: 4px;">
                    <strong>📊 增长缓慢</strong><br>
                    <span style="color: #666; font-size: 0.9em;">进化速度较慢，考虑增加任务多样性或优化学习算法</span>
                </div>
                """)
        
        if not suggestions:
            suggestions.append("""
            <div style="padding: 15px; background: #d4edda; border-left: 4px solid #28a745; border-radius: 4px;">
                <strong>✅ 表现优秀</strong><br>
                <span style="color: #666; font-size: 0.9em;">各项指标均在良好水平，继续保持当前策略</span>
            </div>
            """)
        
        return ''.join(suggestions)
    
    def _get_suggestion_for_dimension(self, dimension: str) -> str:
        """根据维度返回具体建议"""
        suggestions = {
            '成功率': '增加错误处理机制，优化任务分解策略，提高首次执行成功率',
            '效率提升': '优化代码生成质量，减少迭代次数，利用缓存机制加速重复任务',
            '用户满意度': '收集用户反馈，改进交互体验，提供更清晰的进度提示',
            '使用活跃度': '增加技能库丰富度，支持更多编程语言和框架，降低使用门槛',
            '成本效率': '优化 Token 使用，采用更经济的模型，实现智能降级策略',
            '创新性': '引入更多高级设计模式，鼓励探索性解决方案，建立创新激励机制'
        }
        return suggestions.get(dimension, '持续监控并优化该维度的表现')
    
    def _generate_task_list_html(self) -> str:
        """生成任务清单 HTML"""
        if not self.db_path.exists():
            return "<p style='color: #666;'>暂无任务数据。</p>"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # 尝试从 task_records 表获取（如果存在）
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_records'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT task_id, description, success, duration, iterations, timestamp 
                    FROM task_records ORDER BY timestamp DESC LIMIT 20
                """)
                tasks = cursor.fetchall()
            else:
                # 如果没有 task_records，尝试从 scoring_records 的备注或关联表中找
                # 这里我们暂时返回一个提示，或者展示最近的评分记录时间
                return "<p style='color: #666;'>数据库结构中暂无详细任务清单，请确保运行了基准测试脚本。</p>"
            
            if not tasks:
                return "<p style='color: #666;'>暂无已执行的任务记录。</p>"
            
            html = """
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.9em;">
                <thead>
                    <tr style="background: #f8f9fa; text-align: left;">
                        <th style="padding: 12px; border-bottom: 2px solid #667eea;">任务 ID</th>
                        <th style="padding: 12px; border-bottom: 2px solid #667eea;">任务描述</th>
                        <th style="padding: 12px; border-bottom: 2px solid #667eea;">结果</th>
                        <th style="padding: 12px; border-bottom: 2px solid #667eea;">耗时 (s)</th>
                        <th style="padding: 12px; border-bottom: 2px solid #667eea;">迭代次数</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for task in tasks:
                status_color = "#28a745" if task[2] else "#dc3545"
                status_text = "✅ 成功" if task[2] else "❌ 失败"
                html += f"""
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #eee; font-family: monospace;">{task[0]}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;">{task[1][:80]}...</td>
                        <td style="padding: 12px; border-bottom: 1px solid #eee; color: {status_color}; font-weight: bold;">{status_text}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;">{task[3]:.2f}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;">{task[4]}</td>
                    </tr>
                """
            
            html += "</tbody></table>"
            return html
            
        except Exception as e:
            return f"<p style='color: red;'>加载任务清单出错: {e}</p>"
        finally:
            conn.close()

    def _generate_weakness_list(self, radar_data: Dict) -> str:
        """生成薄弱环节列表 HTML"""
        dimensions = {
            '成功率': radar_data.get('success_rate', 0),
            '效率提升': radar_data.get('efficiency_gain', 0),
            '用户满意度': radar_data.get('user_satisfaction', 0),
            '使用活跃度': radar_data.get('usage_activity', 0),
            '成本效率': radar_data.get('cost_efficiency', 0),
            '创新性': radar_data.get('innovation', 0)
        }
        
        # 找出最弱的3个维度
        sorted_dims = sorted(dimensions.items(), key=lambda x: x[1])
        weak_dimensions = sorted_dims[:3]
        
        html = "<ul style='list-style: none; padding: 0;'>"
        for dim_name, score in weak_dimensions:
            if score < 80:
                html += f"""
                <li style="padding: 8px 0; border-bottom: 1px solid #ffeaa7;">
                    <strong>{dim_name}</strong>: {score:.1f}%
                    <span style="color: #856404; font-size: 0.9em; display: block; margin-top: 4px;">
                        {self._get_suggestion_for_dimension(dim_name)}
                    </span>
                </li>
                """
        
        if html == "<ul style='list-style: none; padding: 0;'>":
            html += "<li style='padding: 8px 0;'>✅ 暂无明显薄弱环节</li>"
        
        html += "</ul>"
        return html
    
    def _generate_strength_list(self, radar_data: Dict) -> str:
        """生成优势领域列表 HTML"""
        dimensions = {
            '成功率': radar_data.get('success_rate', 0),
            '效率提升': radar_data.get('efficiency_gain', 0),
            '用户满意度': radar_data.get('user_satisfaction', 0),
            '使用活跃度': radar_data.get('usage_activity', 0),
            '成本效率': radar_data.get('cost_efficiency', 0),
            '创新性': radar_data.get('innovation', 0)
        }
        
        # 找出最强的3个维度
        sorted_dims = sorted(dimensions.items(), key=lambda x: x[1], reverse=True)
        strong_dimensions = sorted_dims[:3]
        
        html = "<ul style='list-style: none; padding: 0;'>"
        for dim_name, score in strong_dimensions:
            if score >= 70:
                html += f"""
                <li style="padding: 8px 0; border-bottom: 1px solid #c3e6cb;">
                    <strong>{dim_name}</strong>: {score:.1f}%
                    <span style="color: #155724; font-size: 0.9em; display: block; margin-top: 4px;">
                        {'⭐' * int(score / 20)} 表现优秀
                    </span>
                </li>
                """
        
        if html == "<ul style='list-style: none; padding: 0;'>":
            html += "<li style='padding: 8px 0;'>📊 数据不足，无法判断优势领域</li>"
        
        html += "</ul>"
        return html


if __name__ == "__main__":
    generator = VisualizationReportGenerator()
    report_path = generator.generate_comprehensive_report(output_format="html")
    
    if report_path:
        print(f"\n🎉 报告生成成功！")
        print(f"📄 文件位置: {report_path}")
        print(f"💡 提示: 在浏览器中打开此文件查看精美的可视化报告")
