"""
Benchmark进度监控脚本
"""
import sqlite3
import os
import time

db_path = "data/holo_half.db"

def check_progress():
    """检查当前进度"""
    if not os.path.exists(db_path):
        print("⏳ 数据库尚未创建，等待中...")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查任务数量
        cursor.execute("SELECT COUNT(*) FROM task_executions")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM task_executions WHERE success = 1")
        success = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM task_executions WHERE success = 0")
        failed = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(duration_seconds) FROM task_executions WHERE duration_seconds > 0")
        avg_duration = cursor.fetchone()[0] or 0
        
        print(f"\n{'='*60}")
        print(f"📊 Benchmark 进度")
        print(f"{'='*60}")
        print(f"总任务数: {total}/15")
        print(f"成功: {success} | 失败: {failed}")
        print(f"平均耗时: {avg_duration:.1f}s")
        
        if total > 0:
            progress = (total / 15) * 100
            print(f"进度: {progress:.0f}%")
            
            if total >= 15:
                print(f"\n✅ Benchmark 完成！")
                return True
        
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"⚠️  检查进度时出错: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    
    return False

if __name__ == "__main__":
    print("🔍 开始监控Benchmark进度...")
    print("按 Ctrl+C 停止监控\n")
    
    try:
        while True:
            if check_progress():
                break
            time.sleep(10)  # 每10秒检查一次
    except KeyboardInterrupt:
        print("\n\n⏹️  监控已停止")
