"""
检查数据库状态并生成示例数据

用于测试可视化报告功能
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random


def check_database():
    """检查数据库表和数据结构"""
    db_path = Path("data/holo_half.db")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("="*70)
    print("📊 数据库状态检查")
    print("="*70)
    print(f"\n📁 数据库文件: {db_path}")
    print(f"📋 表列表: {tables}")
    
    # 检查关键表
    required_tables = ['scoring_records', 'ab_test_results', 'user_behaviors']
    
    for table in required_tables:
        if table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table}: {count} 条记录")
        else:
            print(f"   ❌ {table}: 表不存在")
    
    conn.close()
    print()
    
    return True


def generate_sample_data():
    """生成示例数据用于测试报告"""
    db_path = Path("data/holo_half.db")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在，无法生成示例数据")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("="*70)
    print("🎲 生成示例数据")
    print("="*70)
    
    # 1. 创建 scoring_records 表（如果不存在）
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
    
    # 2. 创建 ab_test_results 表（如果不存在）
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
    
    # 3. 创建 user_behaviors 表（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_behaviors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,
            event_type TEXT,
            event_data TEXT
        )
    """)
    
    conn.commit()
    
    # 生成评分记录（最近 30 天）
    print("\n📝 生成评分记录...")
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        timestamp = date.strftime("%Y-%m-%d %H:%M:%S")
        
        # 模拟进化趋势（分数逐渐提升）
        progress_factor = i / 30.0
        
        overall_score = 0.65 + progress_factor * 0.25 + random.uniform(-0.05, 0.05)
        usage_activity = 0.70 + progress_factor * 0.20 + random.uniform(-0.05, 0.05)
        success_rate = 0.60 + progress_factor * 0.30 + random.uniform(-0.05, 0.05)
        efficiency_gain = 0.55 + progress_factor * 0.35 + random.uniform(-0.05, 0.05)
        user_satisfaction = 0.75 + progress_factor * 0.15 + random.uniform(-0.05, 0.05)
        cost_efficiency = 0.65 + progress_factor * 0.25 + random.uniform(-0.05, 0.05)
        innovation = 0.50 + progress_factor * 0.40 + random.uniform(-0.05, 0.05)
        
        # 确保在 0-1 范围内
        scores = [overall_score, usage_activity, success_rate, efficiency_gain,
                 user_satisfaction, cost_efficiency, innovation]
        scores = [max(0.0, min(1.0, s)) for s in scores]
        
        cursor.execute("""
            INSERT INTO scoring_records 
            (timestamp, overall_score, usage_activity, success_rate, 
             efficiency_gain, user_satisfaction, cost_efficiency, innovation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, *scores))
    
    print(f"   ✅ 已生成 30 条评分记录")
    
    # 生成 A/B 测试结果
    print("\n🧪 生成 A/B 测试结果...")
    
    ab_tests = [
        ("prompt_v1", "prompt_v2", 0.72, 0.85, 0.023, True),
        ("skill_basic", "skill_advanced", 0.68, 0.79, 0.045, True),
        ("model_gpt3", "model_gpt4", 0.75, 0.88, 0.012, True),
        ("strategy_conservative", "strategy_aggressive", 0.80, 0.77, 0.234, False),
        ("workflow_sequential", "workflow_parallel", 0.70, 0.82, 0.031, True),
    ]
    
    for test in ab_tests:
        cursor.execute("""
            INSERT INTO ab_test_results 
            (variant_a_name, variant_b_name, variant_a_score, variant_b_score, 
             p_value, is_significant, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (*test, (datetime.now() - timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S")))
    
    print(f"   ✅ 已生成 {len(ab_tests)} 条 A/B 测试结果")
    
    # 生成用户行为记录
    print("\n👤 生成用户行为记录...")
    
    event_types = ["task_start", "task_complete", "skill_use", "error_occurred", "feedback_submit"]
    
    for i in range(50):
        timestamp = (datetime.now() - timedelta(hours=random.randint(1, 720))).strftime("%Y-%m-%d %H:%M:%S")
        user_id = f"user_{random.randint(1, 5)}"
        event_type = random.choice(event_types)
        event_data = f'{{"detail": "Sample event {i}"}}'
        
        cursor.execute("""
            INSERT INTO user_behaviors (timestamp, user_id, event_type, event_data)
            VALUES (?, ?, ?, ?)
        """, (timestamp, user_id, event_type, event_data))
    
    print(f"   ✅ 已生成 50 条用户行为记录")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print("✅ 示例数据生成完成！")
    print("="*70)


def main():
    """主函数"""
    # 1. 检查数据库
    check_database()
    
    # 2. 询问是否生成示例数据
    response = input("\n💡 是否生成示例数据用于测试报告？(y/n): ").strip().lower()
    
    if response == 'y':
        generate_sample_data()
        print("\n🎉 现在可以运行 python generate_report.py 生成报告了！")
    else:
        print("\n⏭️  跳过示例数据生成")


if __name__ == "__main__":
    main()
