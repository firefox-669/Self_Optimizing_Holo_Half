"""
SOHH 通用进化报告生成器

任何接入 SOHH 的项目都可以使用此脚本，根据自己的 agent_id 
生成包含六维评估、决策透明度和改进建议的完整 HTML 报告。
"""

import sys
import os
from pathlib import Path

# 确保能导入 SOHH 模块
sys.path.append(str(Path(__file__).parent))

from user_scoring.visualization_report import VisualizationReportGenerator
from data_analytics_engine import DataAnalyticsEngine
import sqlite3


def get_agent_data(agent_id: str, db_path: str = "data/holo_half.db"):
    """从数据库中提取指定 Agent 的评估数据"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 获取最新的能力快照 (用于雷达图)
        cursor.execute("""
            SELECT success_rate, efficiency_gain, user_satisfaction, 
                   usage_activity, cost_efficiency, innovation, overall_score
            FROM capability_snapshots 
            WHERE agent_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (agent_id,))
        snapshot = cursor.fetchone()
        
        if not snapshot:
            print(f"⚠️ 数据库中未找到 Agent '{agent_id}' 的数据。")
            return None
            
        radar_data = {
            'success_rate': snapshot[0],
            'efficiency_gain': snapshot[1],
            'user_satisfaction': snapshot[2],
            'usage_activity': snapshot[3],
            'cost_efficiency': snapshot[4],
            'innovation': snapshot[5]
        }
        
        # 2. 获取历史趋势 (用于折线图)
        cursor.execute("""
            SELECT timestamp, overall_score FROM capability_snapshots 
            WHERE agent_id = ? ORDER BY timestamp ASC
        """, (agent_id,))
        history_rows = cursor.fetchall()
        
        trend_data = {
            'labels': [row[0].split('T')[0] for row in history_rows], # 只取日期
            'values': [row[1] for row in history_rows]
        }
        
        conn.close()
        
        return {
            'agent_id': agent_id,
            'radar_data': radar_data,
            'trend_data': trend_data,
            'overall_score': snapshot[6]
        }
        
    except Exception as e:
        print(f"❌ 读取数据库失败: {e}")
        return None


def main():
    # 默认使用 openhands-v1.0，可以通过命令行参数修改
    # 例如: python generate_evolution_report.py openspace-v1.0
    agent_id = sys.argv[1] if len(sys.argv) > 1 else "openhands-v1.0"
    db_path = "data/holo_half.db"
    
    print(f"🔍 正在为 Agent '{agent_id}' 生成 6D 进化报告...")
    
    # 1. 获取数据
    data = get_agent_data(agent_id, db_path)
    if not data:
        print("💡 提示：请先运行集成示例或采集插件产生一些数据。")
        return

    # 2. 初始化报告生成器
    generator = VisualizationReportGenerator(db_path=db_path)
    
    # 3. 生成报告
    report_path = generator.generate_comprehensive_report(
        agent_id=agent_id,
        output_format="html"
    )
    
    if report_path:
        print(f"✅ 报告生成成功！")
        print(f"📂 文件路径: {report_path}")
        print(f"🌐 请在浏览器中打开查看六维评估详情。")
    else:
        print("❌ 报告生成失败。")


if __name__ == "__main__":
    main()
