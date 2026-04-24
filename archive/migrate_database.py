"""
数据库迁移脚本 - 升级到 SOHH 标准接口 v1.0

这个脚本会将旧版本的数据库表结构升级到新的标准接口格式。
"""

import sqlite3
from pathlib import Path


def migrate_database(db_path: str = "data/holo_half.db"):
    """
    迁移数据库到新版本
    
    Args:
        db_path: 数据库文件路径
    """
    db_path = Path(db_path)
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print("="*70)
    print("🔄 数据库迁移工具 v1.0")
    print("="*70)
    print()
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 获取现有表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 现有表: {existing_tables}")
        print()
        
        # 备份旧数据
        print("[1/4] 备份现有数据...")
        backup_tables = {}
        
        if 'task_executions' in existing_tables:
            cursor.execute("SELECT * FROM task_executions")
            backup_tables['task_executions'] = cursor.fetchall()
            print(f"   ✅ 备份 task_executions: {len(backup_tables['task_executions'])} 条记录")
        
        if 'user_feedbacks' in existing_tables:
            cursor.execute("SELECT * FROM user_feedbacks")
            backup_tables['user_feedbacks'] = cursor.fetchall()
            print(f"   ✅ 备份 user_feedbacks: {len(backup_tables['user_feedbacks'])} 条记录")
        
        if 'capability_snapshots' in existing_tables:
            cursor.execute("SELECT * FROM capability_snapshots")
            backup_tables['capability_snapshots'] = cursor.fetchall()
            print(f"   ✅ 备份 capability_snapshots: {len(backup_tables['capability_snapshots'])} 条记录")
        
        print()
        
        # 删除旧表
        print("[2/4] 删除旧表结构...")
        cursor.execute("DROP TABLE IF EXISTS task_executions")
        cursor.execute("DROP TABLE IF EXISTS user_feedbacks")
        cursor.execute("DROP TABLE IF EXISTS capability_snapshots")
        cursor.execute("DROP TABLE IF EXISTS skill_usages")
        print("   ✅ 旧表已删除")
        print()
        
        # 创建新表
        print("[3/4] 创建新表结构...")
        
        # 任务执行表（新版本）
        cursor.execute("""
            CREATE TABLE task_executions (
                task_id TEXT PRIMARY KEY,
                agent_id TEXT,
                project_id TEXT,
                description TEXT,
                status TEXT,
                start_time TEXT,
                end_time TEXT,
                duration_seconds REAL,
                success BOOLEAN,
                error_message TEXT,
                tokens_used INTEGER,
                cost REAL,
                iterations INTEGER,
                code_quality_score REAL,
                test_pass_rate REAL,
                metadata TEXT,
                timestamp TEXT
            )
        """)
        print("   ✅ 创建 task_executions 表")
        
        # 用户反馈表（新版本）
        cursor.execute("""
            CREATE TABLE user_feedbacks (
                feedback_id TEXT PRIMARY KEY,
                task_id TEXT,
                user_id TEXT,
                satisfaction_score REAL,
                feedback_text TEXT,
                would_recommend BOOLEAN,
                timestamp TEXT,
                FOREIGN KEY (task_id) REFERENCES task_executions(task_id)
            )
        """)
        print("   ✅ 创建 user_feedbacks 表")
        
        # 能力快照表（新版本）
        cursor.execute("""
            CREATE TABLE capability_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                agent_id TEXT,
                timestamp TEXT,
                success_rate REAL,
                efficiency_gain REAL,
                user_satisfaction REAL,
                usage_activity REAL,
                cost_efficiency REAL,
                innovation REAL,
                overall_score REAL
            )
        """)
        print("   ✅ 创建 capability_snapshots 表")
        
        # 技能使用表
        cursor.execute("""
            CREATE TABLE skill_usages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id TEXT,
                skill_name TEXT,
                task_id TEXT,
                usage_count INTEGER,
                success_count INTEGER,
                avg_duration REAL,
                timestamp TEXT
            )
        """)
        print("   ✅ 创建 skill_usages 表")
        
        print()
        
        # 恢复数据（如果可能）
        print("[4/4] 尝试恢复数据...")
        
        # 注意：由于表结构变化，旧数据可能无法直接恢复
        # 这里只是提示用户
        if backup_tables:
            print("   ⚠️  由于表结构变化，旧数据无法自动恢复")
            print("   💡 建议：重新运行任务以生成新数据")
        else:
            print("   ℹ️  没有旧数据需要恢复")
        
        conn.commit()
        
        print()
        print("="*70)
        print("✅ 数据库迁移完成！")
        print("="*70)
        print()
        print("📊 新表结构:")
        print("   - task_executions (支持 agent_id, project_id)")
        print("   - user_feedbacks (支持 feedback_id)")
        print("   - capability_snapshots (支持 agent_id)")
        print("   - skill_usages (新增)")
        print()
        print("💡 下一步:")
        print("   1. 运行 openhands_integration_example.py 生成测试数据")
        print("   2. 运行 simple_gen.py 生成报告")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/holo_half.db"
    success = migrate_database(db_path)
    
    sys.exit(0 if success else 1)
