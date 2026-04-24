import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import os

class HoloReportGenerator:
    """生成具有视觉冲击力的全息进化报告"""

    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_holo_dashboard(self, scores: dict, history: list = None, weights: dict = None, filename=None):
        """生成包含雷达图和趋势图的完整 HTML 仪表盘"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"holo_evolution_report_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)

        # 1. 创建雷达图 (当前能力分布)
        categories = ['成功率', '效率', '满意度', '技能有效性', '错误处理', '集成度']
        keys = ['success_rate', 'efficiency', 'satisfaction', 'skill_effectiveness', 'error_handling', 'integration']
        values = [scores.get(k, 0) for k in keys]
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='当前能力指数',
            line_color='#00d2ff'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=False,
            title="🧬 全息能力雷达 (Holo-Capability Radar)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )

        # 2. 创建趋势图 (如果存在历史数据)
        fig_trend = None
        if history and len(history) > 1:
            df = pd.DataFrame(history)
            df['index'] = range(len(df))
            fig_trend = go.Figure()
            for col in categories:
                if col in df.columns:
                    fig_trend.add_trace(go.Scatter(x=df['index'], y=df[col], name=col))
            fig_trend.update_layout(
                title="📈 自进化趋势 (Evolution Trend)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                xaxis_title="迭代次数",
                yaxis_title="评分"
            )

        # 3. 生成透明度表格行
        dimension_rows = ""
        weakness_list = ""
        strength_list = ""
        default_weights = weights or {k: 1/6 for k in keys}
        
        for i, key in enumerate(keys):
            raw_score = scores.get(key, 0)
            weight = default_weights.get(key, 0)
            contribution = raw_score * weight
            dimension_rows += f"""
            <tr style="border-bottom: 1px solid #334155;">
                <td style="padding: 10px;">{categories[i]}</td>
                <td style="padding: 10px; color: {'#4ade80' if raw_score > 0.7 else '#f87171' if raw_score < 0.4 else 'white'}">{raw_score:.3f}</td>
                <td style="padding: 10px;">{(weight * 100):.0f}%</td>
                <td style="padding: 10px;">{contribution:.3f}</td>
            </tr>
            """
            
            # 识别强弱项
            item_html = f"<li style='padding: 5px 0;'>{categories[i]} ({raw_score:.2f})</li>"
            if raw_score < 0.5:
                weakness_list += item_html
            elif raw_score > 0.7:
                strength_list += item_html

        if not weakness_list: weakness_list = "<li style='color: #4ade80;'>暂无明显薄弱环节 🎉</li>"
        if not strength_list: strength_list = "<li style='color: #94a3b8;'>仍有提升空间 💪</li>"

        # 4. 组装 HTML
        html_content = f"""
        <html>
        <head>
            <title>SOHH 全息进化报告</title>
            <style>
                body {{ background-color: #0f172a; color: white; font-family: sans-serif; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ text-align: center; margin-bottom: 40px; border-bottom: 1px solid #334155; padding-bottom: 20px; }}
                .score-card {{ background: #1e293b; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
                .big-score {{ font-size: 4em; font-weight: bold; color: #00d2ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Self_Optimizing_Holo_Half 评估报告</h1>
                    <p>生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <div class="score-card">
                    <div>综合进化指数</div>
                    <div class="big-score">{scores.get('overall', 0):.2f}</div>
                </div>

                <div style="display: flex; flex-wrap: wrap; justify-content: space-around; margin-top: 30px;">
                    <div style="width: 45%; min-width: 400px;">
                        {fig_radar.to_html(full_html=False, include_plotlyjs='cdn')}
                    </div>
                    <div style="width: 45%; min-width: 400px;">
                        {fig_trend.to_html(full_html=False, include_plotlyjs='cdn') if fig_trend else '<div style="text-align:center; padding:50px; color:#94a3b8;">需要更多历史数据以生成趋势图</div>'}
                    </div>
                </div>

                <div class="score-card" style="margin-top: 30px; text-align: left;">
                    <h2 style="color: #00d2ff; border-bottom: 1px solid #334155; padding-bottom: 10px;">🔍 决策透明度报告 (Decision Transparency)</h2>
                    <table style="width: 100%; border-collapse: collapse; color: #cbd5e1;">
                        <thead>
                            <tr style="background: #1e293b; text-align: left;">
                                <th style="padding: 12px;">评估维度</th>
                                <th style="padding: 12px;">原始得分</th>
                                <th style="padding: 12px;">权重</th>
                                <th style="padding: 12px;">加权贡献</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dimension_rows}
                        </tbody>
                    </table>
                </div>

                <div class="score-card" style="margin-top: 30px; text-align: left;">
                    <h2 style="color: #fbbf24; border-bottom: 1px solid #334155; padding-bottom: 10px;">⚡ 关键影响因素 (Key Influencing Factors)</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <h3 style="font-size: 1.1em; color: #94a3b8;">📉 薄弱环节 (Weaknesses)</h3>
                            <ul style="list-style: none; padding: 0;">
                                {weakness_list}
                            </ul>
                        </div>
                        <div>
                            <h3 style="font-size: 1.1em; color: #94a3b8;">🚀 优势领域 (Strengths)</h3>
                            <ul style="list-style: none; padding: 0;">
                                {strength_list}
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="score-card" style="margin-top: 30px; text-align: left; font-size: 0.9em; color: #94a3b8;">
                    <h2 style="color: #64748b; border-bottom: 1px solid #334155; padding-bottom: 10px;">📖 评估算法定义 (Algorithm Definitions)</h2>
                    <details style="margin-bottom: 10px;">
                        <summary style="cursor: pointer; color: #cbd5e1; font-weight: bold;">✅ 成功率 (Success Rate) 是如何计算的？</summary>
                        <p style="padding: 10px; background: #0f172a; border-radius: 5px; margin-top: 5px;">
                            <strong>公式：</strong> (成功执行的任务数 / 总任务数)<br>
                            <strong>数据来源：</strong> 拦截自 Agent 的执行日志。<br>
                            <strong>示例：</strong> 如果最近跑了 10 个任务，有 10 个返回了 "success"，则得分为 1.0。
                        </p>
                    </details>
                    <details style="margin-bottom: 10px;">
                        <summary style="cursor: pointer; color: #cbd5e1; font-weight: bold;">⚡ 效率 (Efficiency) 是如何计算的？</summary>
                        <p style="padding: 10px; background: #0f172a; border-radius: 5px; margin-top: 5px;">
                            <strong>公式：</strong> 1 - (实际耗时 / 预设基准耗时)<br>
                            <strong>数据来源：</strong> 记录每个 Action 的开始与结束时间戳。<br>
                            <strong>说明：</strong> 耗时越短，分数越高；若超过基准时间，分数将线性下降。
                        </p>
                    </details>
                    <details>
                        <summary style="cursor: pointer; color: #cbd5e1; font-weight: bold;">🛡️ 错误处理 (Error Handling) 是如何计算的？</summary>
                        <p style="padding: 10px; background: #0f172a; border-radius: 5px; margin-top: 5px;">
                            <strong>逻辑：</strong> 检测日志中是否包含 "Traceback" 或 "Exception"。<br>
                            <strong>加分项：</strong> 如果系统在报错后自动触发了重试或修复逻辑，将获得额外加分。
                        </p>
                    </details>
                </div>
            </div>
        </body>
        </html>
        """

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
