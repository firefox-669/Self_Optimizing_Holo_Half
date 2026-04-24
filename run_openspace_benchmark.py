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
    
    # 2. 定义要测试的真实任务列表
    tasks = [
        "Write a Python script to calculate the Fibonacci sequence up to 100 terms.",
        "Create a simple HTML page with a button that changes color when clicked.",
        "Refactor the following code to use list comprehension: [x for x in range(10) if x % 2 == 0]"
    ]
    
    try:
        # 3. 导入并初始化 OpenSpace (配置为中国移动 MaaS 平台)
        from openspace.tool_layer import OpenSpace, OpenSpaceConfig
        from dotenv import load_dotenv
        load_dotenv() # 加载 .env 文件
        
        config = OpenSpaceConfig(
            llm_model="openai/minimax-m25", # 添加 openai/ 前缀以适配 LiteLLM
            llm_kwargs={
                "base_url": os.getenv("OPENAI_BASE_URL"),
                "api_key": os.getenv("OPENAI_API_KEY")
            }
        )
        agent = OpenSpace(config=config)
        
        print("⚙️  正在初始化 OpenSpace 引擎...")
        await agent.initialize()
        
        for i, task_desc in enumerate(tasks):
            task_id = f"real-os-task-{i+1}"
            print(f"\n[{i+1}/{len(tasks)}] 正在执行任务: {task_desc[:50]}...")
            
            # [接入点 1] 记录任务开始
            collector.start_task(task_id=task_id, description=task_desc)
            start_time = time.time()
            
            try:
                # 执行真实任务
                result = await agent.execute(task=task_desc, max_iterations=10)
                
                duration = time.time() - start_time
                status = result.get('status', 'unknown')
                success = (status == 'success')
                
                # [接入点 2] 记录任务结束
                collector.end_task(
                    task_id=task_id,
                    success=success,
                    iterations=result.get('iterations', 0),
                    error_message=result.get('error') if not success else None
                )
                
                print(f"   ✅ 任务完成 (状态: {status}, 耗时: {duration:.2f}s)")
                
            except Exception as e:
                duration = time.time() - start_time
                print(f"   ❌ 任务失败: {e}")
                collector.end_task(task_id=task_id, success=False, error_message=str(e))
        
        # 4. 提交所有数据到 SOHH 数据库
        db_path = os.path.join(os.path.dirname(__file__), "data", "holo_half.db")
        collector.submit_to_sohh(db_path=db_path)
        print(f"\n✅ 真实测试数据已同步至 SOHH 数据库!")
        
    except ImportError:
        print("⚠️  未找到 openspace 模块，请确保在正确的环境下运行。")
    except Exception as e:
        print(f"❌ 运行过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_real_openspace_benchmark())
