"""
OpenSpace 真实集成模块 (Real Integration for OpenSpace)

=============================================================================
🚀 SOHH 接入指南 (Integration Guide)
=============================================================================

1. 【复制文件】
   将此文件 (integration_openspace_real.py) 复制到 OpenSpace 项目的根目录。

2. 【修改核心逻辑】
   找到 OpenSpace 执行任务的主函数（通常在 openspace/agents/ 或 tool_layer.py）。
   在任务执行的 try...except 块中加入以下代码：

   from integration_openspace_real import monitor

   def execute_task(task_desc):
       task_id = str(uuid.uuid4())
       
       # [接入点 1] 记录开始
       monitor.on_task_start(task_id, task_desc)
       
       try:
           # ... 原有的 OpenSpace 执行逻辑 ...
           result = run_agent(task_desc)
           
           # [接入点 2] 记录成功
           monitor.on_task_end(
               task_id=task_id, 
               success=True, 
               tokens_used=result.tokens, 
               cost=result.cost
           )
           return result
           
       except Exception as e:
           # [接入点 3] 记录失败
           monitor.on_task_end(task_id=task_id, success=False)
           raise e

3. 【生成报告】
   运行几个任务后，进入 Self_Optimizing_Holo_Half 目录运行：
   python generate_evolution_report.py openspace-v1.0

=============================================================================
"""

import sys
import os
import time
from datetime import datetime

# --- 核心：导入 SOHH 标准接口 ---
# 自动寻找 SOHH 模块，支持不同目录结构
try:
    # 尝试方法 1: 如果 SOHH 在上一级目录 (例如: Parent/SOHH & Parent/OpenSpace)
    sohh_path = os.path.join(os.path.dirname(__file__), '..', 'Self_Optimizing_Holo_Half')
    
    # 尝试方法 2: 如果 SOHH 在更远的地方，你可以手动在这里修改绝对路径
    # sohh_path = r"H:\Your\Path\To\Self_Optimizing_Holo_Half"
    
    if os.path.exists(sohh_path) and sohh_path not in sys.path:
        sys.path.insert(0, os.path.abspath(sohh_path))
        
    from sohh_standard_interface import create_collector
    print(f"✅ SOHH 模块加载成功 (路径: {sohh_path})")
except ImportError:
    print("⚠️ 警告: 未找到 SOHH 模块。请检查 integration_openspace_real.py 中的 sohh_path 设置。")
    create_collector = None


class OpenSpaceSOHHMonitor:
    """OpenSpace 的 SOHH 监控器"""
    
    def __init__(self, project_id="openspace-production"):
        if create_collector:
            self.collector = create_collector(agent_id="openspace-v1.0", project_id=project_id)
            print("✅ SOHH 监控已启动：正在记录 OpenSpace 的执行表现...")
        else:
            self.collector = None

    def on_task_start(self, task_id, description):
        """在任务开始时调用"""
        if self.collector:
            self.collector.start_task(task_id=str(task_id), description=description)

    def on_task_end(self, task_id, success, tokens_used=0, cost=0.0, duration=0.0):
        """在任务结束时调用"""
        if self.collector:
            self.collector.end_task(
                task_id=str(task_id),
                success=success,
                tokens_used=tokens_used,
                cost=cost,
                iterations=1
            )
            # 实时同步（也可以改为定期同步以节省性能）
            self.collector.submit_to_sohh(db_path=os.path.join(sohh_path, "data", "holo_half.db"))

    def on_feedback(self, task_id, score, comment=""):
        """当用户给出反馈时调用"""
        if self.collector:
            self.collector.record_feedback(task_id=str(task_id), satisfaction_score=score, feedback_text=comment)


# --- 全局单例，方便在任何地方调用 ---
monitor = OpenSpaceSOHHMonitor()
