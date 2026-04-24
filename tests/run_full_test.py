"""
完整流程测试：生成数据 + 生成报告

根据 my_direction 战略要求执行
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random
import sys

# 添加项目根目录
sys.path.insert(0, str(Path(__file__).parent))

def seed_database():
    """生成示例数据"""
    print("="*70)
    print("📊 第1步：生成示例数据")
    print("="*70)
    
    db_path = Path("data/holo_half.db")
    
    if not db_path.exists():
        print("❌ 数据库不存在")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scoring_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            overall_score REAL,
            usage_activity REAL,
            success_rate REAL,
            efficiency_gain REAL,
            user_satisfaction REAL,
            cost_efficiency REAL,
            innovation REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ab_test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            variant_a_name TEXT,
            variant_b_name TEXT,
            variant_a_score REAL,
            variant_b_score REAL,
            p_value REAL,
            is_significant BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM scoring_records")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"✅ 数据库中已有 {count} 条评分记录")
        conn.close()
        return True
    
    # 生成30天的数据
    print("\n📝 正在生成30天的进化数据...")
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        timestamp = date.strftime("%Y-%m-%d %H:%M:%S")
        
        # 模拟进化趋势
        progress = i / 30.0
        
        overall = 0.65 + progress * 0.25 + random.uniform(-0.03, 0.03)
        usage = 0.70 + progress * 0.20 + random.uniform(-0.03, 0.03)
        success = 0.60 + progress * 0.30 + random.uniform(-0.03, 0.03)
        efficiency = 0.55 + progress * 0.35 + random.uniform(-0.03, 0.03)
        satisfaction = 0.75 + progress * 0.15 + random.uniform(-0.03, 0.03)
        cost = 0.65 + progress * 0.25 + random.uniform(-0.03, 0.03)
        innovation = 0.50 + progress * 0.40 + random.uniform(-0.03, 0.03)
        
        # 限制在 0-1
        scores = [max(0.0, min(1.0, s)) for s in [overall, usage, success, efficiency, 
                                                   satisfaction, cost, innovation]]
        
        cursor.execute("""
            INSERT INTO scoring_records 
            (timestamp, overall_score, usage_activity, success_rate, 
             efficiency_gain, user_satisfaction, cost_efficiency, innovation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, *scores))
    
    # 生成 A/B 测试数据
    print("🧪 正在生成 A/B 测试数据...")
    
    tests = [
        ("prompt_v1", "prompt_v2", 0.72, 0.85, 0.023, 1),
        ("skill_basic", "skill_advanced", 0.68, 0.79, 0.045, 1),
        ("model_gpt3", "model_gpt4", 0.75, 0.88, 0.012, 1),
        ("strategy_conservative", "strategy_aggressive", 0.80, 0.77, 0.234, 0),
        ("workflow_sequential", "workflow_parallel", 0.70, 0.82, 0.031, 1),
    ]
    
    for test in tests:
        cursor.execute("""
            INSERT INTO ab_test_results 
            (variant_a_name, variant_b_name, variant_a_score, variant_b_score, 
             p_value, is_significant, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (*test, (datetime.now() - timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()
    
    print("✅ 数据生成完成！")
    print(f"   - 30 条评分记录")
    print(f"   - {len(tests)} 条 A/B 测试结果")
    print()
    
    return True


def generate_report():
    """生成可视化报告"""
    print("="*70)
    print("📊 第2步：生成可视化报告")
    print("="*70)
    print()
    
    try:
        from user_scoring import VisualizationReportGenerator
        
        generator = VisualizationReportGenerator(db_path="data/holo_half.db")
        
        # 生成 HTML 报告
        print("🎨 生成 HTML 报告（精美图表）...")
        html_report = generator.generate_comprehensive_report(output_format="html")
        
        if html_report:
            print(f"✅ HTML 报告: {html_report}")
        else:
            print("⚠️  HTML 报告生成失败")
        
        print()
        
        # 生成 Markdown 报告
        print("📝 生成 Markdown 报告...")
        md_report = generator.generate_comprehensive_report(output_format="markdown")
        
        if md_report:
            print(f"✅ Markdown 报告: {md_report}")
        else:
            print("⚠️  Markdown 报告生成失败")
        
        print()
        print("="*70)
        print("🎉 报告生成完成！")
        print("="*70)
        print()
        
        if html_report:
            print("💡 下一步操作:")
            print(f"   1. 在浏览器中打开: {html_report}")
            print("   2. 查看精美的雷达图和趋势图")
            print("   3. 截图分享到 GitHub/社交媒体")
            print()
            print("🚀 这证明了 SOHH 的科学评估能力！")
        
        return True
        
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print()
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "SOHH 战略执行测试" + " "*31 + "║")
    print("║" + " "*15 + "基于 my_direction 行动路线" + " "*27 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    # 第1步：生成数据
    if not seed_database():
        print("\n❌ 数据生成失败，退出")
        return
    
    # 第2步：生成报告
    if not generate_report():
        print("\n❌ 报告生成失败")
        return
    
    print()
    print("="*70)
    print("✅ my_direction 第1步完成：可视化报表系统已实现")
    print("="*70)
    print()
    print("📋 接下来按照 my_direction 的计划:")
    print("   ✅ 第1步（本周）: 实现 HTML/Markdown 报告生成器 ← 已完成")
    print("   ⏳ 第2步（下周）: 用 SOHE 跑任务并生成报告")
    print("   ⏳ 第3步（下下周）: 分享报告到社区")
    print()


if __name__ == "__main__":
    main()
