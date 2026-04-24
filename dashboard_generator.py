"""
SOHH 可视化 Dashboard 生成器

该模块负责将标准化的进化建议报告 (StandardEvolutionReport) 
转化为美观的 HTML 交互界面。
"""

from sohh_standard_interface import StandardEvolutionReport, StandardActionItem
from datetime import datetime
import json


class DashboardGenerator:
    def __init__(self):
        pass

    def generate_dashboard(self, report: StandardEvolutionReport, output_path: str = "sohh_dashboard.html", db_path: str = "data/holo_half.db"):
        """生成完整的 HTML Dashboard"""
        
        # 准备雷达图数据：从数据库动态获取
        radar_data = self._extract_radar_data(report.agent_id, db_path)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SOHH Agent Evolution Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                :root {{ --primary: #6366f1; --bg: #f8fafc; --card-bg: #ffffff; }}
                body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding: 20px; color: #334155; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
                .card {{ background: var(--card-bg); border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }}
                .score-circle {{ width: 150px; height: 150px; border-radius: 50%; background: conic-gradient(var(--primary) {report.current_health_score * 3.6}deg, #e2e8f0 0deg); display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
                .score-inner {{ width: 120px; height: 120px; background: white; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
                .score-num {{ font-size: 2.5em; font-weight: bold; color: var(--primary); }}
                .action-item {{ border-left: 4px solid var(--primary); padding: 15px; margin-bottom: 15px; background: #f1f5f9; border-radius: 0 8px 8px 0; }}
                .priority-high {{ border-color: #ef4444; }}
                .priority-medium {{ border-color: #f59e0b; }}
                .tag {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; background: #e0e7ff; color: #4338ca; margin-right: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 SOHH Agent Evolution Dashboard</h1>
                    <p>Agent ID: {report.agent_id} | Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M')}</p>
                </div>

                <div class="grid">
                    <!-- 左侧：健康度与雷达图 -->
                    <div class="card">
                        <h2 style="text-align: center;">💯 综合能力评估</h2>
                        <div class="score-circle">
                            <div class="score-inner">
                                <span class="score-num">{report.current_health_score:.1f}</span>
                                <span style="font-size: 0.9em; color: #64748b;">Health Score</span>
                            </div>
                        </div>
                        <canvas id="radarChart" style="margin-top: 20px;"></canvas>
                    </div>

                    <!-- 右侧：进化建议清单 -->
                    <div class="card">
                        <h2>💡 进化建议 (Action Items)</h2>
                        <div id="suggestions-list">
                            {self._generate_suggestions_html(report.action_items)}
                        </div>
                    </div>
                </div>

                <!-- 底部：行业趋势参考 -->
                <div class="card">
                    <h2>🌍 行业技术趋势参考</h2>
                    <ul style="list-style-type: none; padding: 0;">
                        {self._generate_trends_html(report.trend_references)}
                    </ul>
                </div>
            </div>

            <script>
                const ctx = document.getElementById('radarChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'radar',
                    data: {{
                        labels: {json.dumps(list(radar_data.keys()))},
                        datasets: [{{
                            label: 'Current Capability',
                            data: {json.dumps(list(radar_data.values()))},
                            fill: true,
                            backgroundColor: 'rgba(99, 102, 241, 0.2)',
                            borderColor: 'rgb(99, 102, 241)',
                            pointBackgroundColor: 'rgb(99, 102, 241)',
                        }}]
                    }},
                    options: {{ scales: {{ r: {{ min: 0, max: 100 }} }} }}
                }});
            </script>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard 已生成: {output_path}")
        return output_path

    def _extract_radar_data(self, agent_id: str, db_path: str = "data/holo_half.db"):
        """从数据库中提取最新的六维评估数据"""
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # 获取该 Agent 最新的一条能力快照
            cursor.execute("""
                SELECT success_rate, efficiency_gain, user_satisfaction, 
                       usage_activity, cost_efficiency, innovation 
                FROM capability_snapshots 
                WHERE agent_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            """, (agent_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "成功率 (Success Rate)": row[0],
                    "效率提升 (Efficiency)": row[1],
                    "用户满意度 (Satisfaction)": row[2],
                    "使用活跃度 (Activity)": row[3],
                    "成本效率 (Cost Eff.)": row[4],
                    "创新性 (Innovation)": row[5]
                }
        except Exception as e:
            print(f"⚠️ 读取数据库失败: {e}")
            
        # 如果数据库没数据，返回默认值
        return {
            "成功率": 0, "效率": 0, "满意度": 0, 
            "活跃度": 0, "成本": 0, "创新": 0
        }

    def _generate_suggestions_html(self, items):
        if not items:
            return "<p>🎉 当前表现优秀，暂无紧急优化建议。</p>"
        
        html = ""
        for item in items:
            priority_class = f"priority-{item.priority.value}"
            html += f"""
            <div class="action-item {priority_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>{item.title}</strong>
                    <span class="tag">{item.category.value}</span>
                </div>
                <p style="margin: 8px 0; font-size: 0.9em; color: #475569;">{item.description}</p>
                <div style="font-size: 0.85em; color: #64748b;">
                    🎯 预期提升: {item.expected_metrics} | 难度: {item.complexity_score}/10
                </div>
            </div>
            """
        return html

    def _generate_trends_html(self, trends):
        if not trends:
            return "<li>暂无最新趋势数据</li>"
        
        html = ""
        for trend in trends:
            html += f"""
            <li style="padding: 10px 0; border-bottom: 1px solid #e2e8f0;">
                <strong>📰 {trend['title']}</strong>
                <p style="margin: 5px 0; font-size: 0.9em; color: #64748b;">{trend['description']}</p>
                <small style="color: #94a3b8;">Source: {trend.get('source', 'SOHH Monitor')}</small>
            </li>
            """
        return html


if __name__ == "__main__":
    from suggestion_engine import SOHHSuggestionEngine
    
    # 1. 获取建议报告
    engine = SOHHSuggestionEngine()
    report = engine.get_evolution_suggestions("openhands-v1.0")
    
    # 2. 生成 Dashboard
    generator = DashboardGenerator()
    generator.generate_dashboard(report)
