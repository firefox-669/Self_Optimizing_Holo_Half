"""
OpenSpace 真实能力评估 - 外部监控脚本
此脚本会实际运行 OpenSpace 引擎，并将表现数据同步给 SOHH
"""
import sys
import os
import asyncio
import time
from datetime import datetime

# 添加路径以便导入 OpenSpace 和 SOHH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')) # 指向 openspace
sys.path.insert(0, os.path.dirname(__file__)) # 指向 sohh

from sohh_standard_interface import SOHHDataCollector

async def run_real_openspace_benchmark():
    print("🚀 正在启动 OpenSpace 真实基准测试...")
    
    # 1. 初始化 SOHH 采集器
    collector = SOHHDataCollector(agent_id="openspace-v1.0", project_id="openspace-official")
    
    # 2. 定义要测试的真实任务列表（15个多样化任务，充分展示能力）
    tasks = [
        # 简单任务 (1-5)
        "Write a Python function to calculate factorial of a number.",
        "Create a HTML page with a heading and paragraph.",
        "Write a SQL query to select all users from a database.",
        "Create a CSS style for a centered div with blue background.",
        "Write a JavaScript function to add two numbers.",
        
        # 中等任务 (6-10)
        "Write a Python script to read a CSV file and count rows by category.",
        "Create a REST API endpoint using Flask that returns JSON data.",
        "Write a Python class for a simple bank account with deposit and withdraw methods.",
        "Create a React component that displays a list of items with delete button.",
        "Write a Python script to download a file from URL and save it locally.",
        
        # 复杂任务 (11-15)
        "Build a Python web scraper that extracts article titles from a news website.",
        "Create a Dockerfile for a Python Flask application with PostgreSQL.",
        "Write a Python script to analyze sentiment of text using NLTK library.",
        "Implement a binary search tree in Python with insert, search, and delete operations.",
        "Create a GitHub Actions workflow to test and deploy a Python package."
    ]
    
    try:
        # 3. 导入并初始化 OpenSpace (配置为中国移动 MaaS 平台)
        from openspace.tool_layer import OpenSpace, OpenSpaceConfig
        from dotenv import load_dotenv
        load_dotenv() # 加载 .env 文件
        
        # 确保日志目录存在且不会被清理
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "recordings"))
        os.makedirs(log_dir, exist_ok=True)
        
        config = OpenSpaceConfig(
            llm_model="openai/minimax-m25",
            llm_kwargs={
                "base_url": os.getenv("OPENAI_BASE_URL"),
                "api_key": os.getenv("OPENAI_API_KEY")
            },
            recording_backends=["shell", "mcp", "system"],
            recording_log_dir=log_dir  # 显式指定录制目录
        )
        agent = OpenSpace(config=config)
        
        print("⚙️  正在初始化 OpenSpace 引擎...")
        await agent.initialize()
        
        for i, task_desc in enumerate(tasks):
            task_id = f"real-os-task-{i+1}"
            print(f"\n{'='*70}")
            print(f"[{i+1}/{len(tasks)}] 正在执行任务:")
            print(f"   {task_desc}")
            print(f"{'='*70}")
            
            # [接入点 1] 记录任务开始
            collector.start_task(task_id=task_id, description=task_desc)
            start_time = time.time()
            
            try:
                # 执行真实任务
                result = await agent.execute(task=task_desc, max_iterations=15)
                
                duration = time.time() - start_time
                status = result.get('status', 'unknown')
                success = (status == 'success')
                
                # 获取 OpenSpace 的真实任务 ID 和日志路径
                real_task_id = result.get('task_id', '')
                log_path = ""
                if real_task_id:
                    # 尝试在 recordings 目录下寻找对应的文件夹
                    base_log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "recordings"))
                    for d in os.listdir(base_log_dir):
                        if real_task_id in d:
                            log_path = os.path.join(base_log_dir, d)
                            break
                
                # [接入点 2] 记录任务结束，并附带真实日志路径
                collector.end_task(
                    task_id=task_id,
                    success=success,
                    iterations=result.get('iterations', 0),
                    error_message=result.get('error') if not success else None,
                    metadata={'real_task_id': real_task_id, 'log_path': log_path}
                )
                
                status_icon = "✅" if success else "❌"
                print(f"\n{status_icon} 任务完成")
                print(f"   状态: {status}")
                print(f"   耗时: {duration:.2f}s")
                print(f"   迭代次数: {result.get('iterations', 0)}")
                if not success:
                    print(f"   错误: {result.get('error', 'Unknown')}")
                
            except Exception as e:
                duration = time.time() - start_time
                print(f"\n❌ 任务失败: {e}")
                import traceback
                traceback.print_exc()
                collector.end_task(task_id=task_id, success=False, error_message=str(e))
        
        # 4. 提交所有数据到 SOHH 数据库
        db_path = os.path.join(os.path.dirname(__file__), "data", "holo_half.db")
        
        # 尝试寻找 OpenSpace 的日志目录
        log_dir = os.path.join(os.path.dirname(__file__), "..", "logs", "recordings")
        if not os.path.exists(log_dir):
            # 备选路径：当前目录下的 logs
            log_dir = os.path.join(os.path.dirname(__file__), "logs", "recordings")
            
        print(f"\n🔍 正在查找链路日志: {log_dir}")
        result = collector.submit_to_sohh(db_path=db_path, trace_source_path=log_dir)
        
        # 拍摄能力快照
        snapshot = collector.take_capability_snapshot()
        
        print(f"\n{'='*70}")
        print(f"✅ Benchmark 完成！")
        print(f"{'='*70}")
        print(f"\n📊 统计摘要:")
        print(f"   总任务数: {len(tasks)}")
        print(f"   成功数: {sum(1 for t in collector.task_executions if t.success)}")
        print(f"   失败数: {sum(1 for t in collector.task_executions if not t.success)}")
        print(f"   成功率: {snapshot.success_rate:.1f}%")
        print(f"   平均耗时: {sum(t.duration_seconds for t in collector.task_executions if t.duration_seconds) / max(1, sum(1 for t in collector.task_executions if t.duration_seconds)):.1f}s")
        print(f"   综合评分: {snapshot.overall_score:.1f}/100")
        print(f"\n💾 数据已保存至: {db_path}")
        print(f"\n📈 下一步: 运行 'python -m user_scoring.visualization_report' 生成报告")
        
    except ImportError:
        print("⚠️  未找到 openspace 模块，请确保在正确的环境下运行。")
    except Exception as e:
        print(f"❌ 运行过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_real_openspace_benchmark())
