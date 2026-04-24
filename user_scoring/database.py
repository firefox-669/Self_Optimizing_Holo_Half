"""
数据库管理器

使用 SQLite 存储用户行为数据、评分数据等
"""

import sqlite3
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class DatabaseManager:
    """SQLite 数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 默认数据库路径: data/holo_half.db
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            self.db_path = str(data_dir / "holo_half.db")
        else:
            self.db_path = db_path
        
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """建立数据库连接"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行 SQL 查询"""
        if not self.conn:
            self.connect()
        cursor = self.conn.execute(query, params)
        self.conn.commit()
        return cursor
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """查询单条记录"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """查询多条记录"""
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def init_db(db_path: str = None):
    """
    初始化数据库 schema
    
    创建所有必要的表
    """
    db = DatabaseManager(db_path)
    db.connect()
    
    try:
        # 1. 任务执行记录表
        db.execute("""
            CREATE TABLE IF NOT EXISTS task_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                user_id TEXT,
                mode TEXT NOT NULL,  -- 'normal' or 'evolution'
                task_type TEXT,      -- 'openhands' or 'openspace'
                instruction TEXT,
                status TEXT NOT NULL,  -- 'success', 'failed', 'timeout'
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds REAL,
                tokens_used INTEGER,
                error_message TEXT,
                skills_used TEXT,  -- JSON array of skill IDs
                metadata TEXT,  -- JSON object
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. 用户反馈表
        db.execute("""
            CREATE TABLE IF NOT EXISTS user_feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                user_id TEXT,
                rating INTEGER,  -- 1-5 stars
                feedback_type TEXT,  -- 'explicit' or 'implicit'
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES task_executions(task_id)
            )
        """)
        
        # 3. Skill 使用统计表
        db.execute("""
            CREATE TABLE IF NOT EXISTS skill_usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id TEXT NOT NULL,
                version TEXT,
                execution_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0,
                avg_duration REAL,
                avg_tokens REAL,
                avg_rating REAL,
                last_used_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(skill_id, version)
            )
        """)
        
        # 4. A/B 测试记录表
        db.execute("""
            CREATE TABLE IF NOT EXISTS ab_test_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                variant TEXT NOT NULL,  -- 'A' or 'B'
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(test_id, user_id)
            )
        """)
        
        # 5. 版本日志表
        db.execute("""
            CREATE TABLE IF NOT EXISTS version_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id TEXT UNIQUE NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                suggestion_source TEXT,  -- JSON
                changes TEXT,  -- JSON
                new_features TEXT,  -- JSON
                evaluation_results TEXT,  -- JSON
                decision TEXT,  -- 'KEEP_AND_PROMOTE', 'KEEP', etc.
                git_commit_hash TEXT,
                rollback_available BOOLEAN DEFAULT 1
            )
        """)
        
        # 6. 能力指标快照表
        db.execute("""
            CREATE TABLE IF NOT EXISTS capability_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT UNIQUE NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metrics TEXT,  -- JSON object with all metrics
                version_id TEXT,
                FOREIGN KEY (version_id) REFERENCES version_logs(version_id)
            )
        """)
        
        # 7. 任务记录表 (用于报告展示)
        db.execute("""
            CREATE TABLE IF NOT EXISTS task_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                description TEXT,
                success BOOLEAN DEFAULT 0,
                duration REAL DEFAULT 0,
                iterations INTEGER DEFAULT 0,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引以提升查询性能
        db.execute("CREATE INDEX IF NOT EXISTS idx_task_executions_user ON task_executions(user_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_task_executions_status ON task_executions(status)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_task_executions_created ON task_executions(created_at)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_user_feedbacks_task ON user_feedbacks(task_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_skill_usage_skill ON skill_usage_stats(skill_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_ab_test_assignments_test ON ab_test_assignments(test_id)")
        
        print(f"✅ Database initialized at {db.db_path}")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # 测试数据库初始化
    init_db()
    print("Database schema created successfully!")
