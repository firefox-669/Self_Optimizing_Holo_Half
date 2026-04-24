"""
OpenHands 与 SOHH 标准接口集成示例

这个文件展示了如何将 OpenHands 的执行数据通过 SOHH 标准接口进行采集。
其他 AI Agent 系统可以参考此示例实现自己的集成。

使用方法：
1. 在 OpenHands 的任务执行流程中引入 SOHHDataCollector
2. 在任务开始/结束时调用相应的记录方法
3. 定期提交数据到 SOHH 数据库
"""

from sohh_standard_interface import SOHHDataCollector, create_collector
from datetime import datetime, timedelta
import time


def simulate_openhands_task_execution():
    """
    模拟 OpenHands 任务执行流程
    
    这只是一个示例，实际使用时需要集成到 OpenHands 的真实执行流程中
    """
    
    print("="*70)
    print("🚀 OpenHands + SOHH 集成示例")
    print("="*70)
    print()
    
    # 1. 创建数据采集器
    print("[1/5] 创建 SOHH 数据采集器...")
    collector = create_collector(
        agent_id="openhands-v1.0",
        project_id="demo-project"
    )
    print("✅ 采集器创建成功")
    print()
    
    # 2. 模拟执行多个任务
    print("[2/5] 模拟执行任务...")
    
    tasks = [
        {
            "task_id": "oh-task-001",
            "description": "Create a Flask REST API with user authentication",
            "duration": 180,  # 秒
            "success": True,
            "tokens": 2500,
            "cost": 0.005,
            "iterations": 3,
            "quality": 0.85,
            "test_rate": 0.90
        },
        {
            "task_id": "oh-task-002",
            "description": "Fix a Python bug in data processing pipeline",
            "duration": 120,
            "success": True,
            "tokens": 1800,
            "cost": 0.0036,
            "iterations": 2,
            "quality": 0.90,
            "test_rate": 0.95
        },
        {
            "task_id": "oh-task-003",
            "description": "Implement machine learning model training script",
            "duration": 300,
            "success": False,
            "tokens": 3500,
            "cost": 0.007,
            "iterations": 5,
            "error": "Timeout error during model training",
            "quality": 0.60,
            "test_rate": 0.70
        },
        {
            "task_id": "oh-task-004",
            "description": "Optimize database query performance",
            "duration": 150,
            "success": True,
            "tokens": 2000,
            "cost": 0.004,
            "iterations": 2,
            "quality": 0.88,
            "test_rate": 0.92
        },
        {
            "task_id": "oh-task-005",
            "description": "Build a React component library",
            "duration": 240,
            "success": True,
            "tokens": 3000,
            "cost": 0.006,
            "iterations": 4,
            "quality": 0.82,
            "test_rate": 0.85
        }
    ]
    
    for i, task_info in enumerate(tasks, 1):
        print(f"   任务 {i}/{len(tasks)}: {task_info['description'][:50]}...")
        
        # 记录任务开始
        collector.start_task(
            task_id=task_info['task_id'],
            description=task_info['description'],
            metadata={
                "framework": "Flask",
                "language": "Python",
                "difficulty": "medium"
            }
        )
        
        # 模拟任务执行
        time.sleep(0.5)  # 模拟执行时间
        
        # 记录技能使用
        collector.record_skill_usage(
            skill_id="code_generation",
            skill_name="Code Generation",
            task_id=task_info['task_id'],
            success=task_info['success'],
            duration=task_info['duration'] * 0.6
        )
        
        collector.record_skill_usage(
            skill_id="debugging",
            skill_name="Debugging",
            task_id=task_info['task_id'],
            success=task_info['success'],
            duration=task_info['duration'] * 0.3
        )
        
        # 记录任务结束
        collector.end_task(
            task_id=task_info['task_id'],
            success=task_info['success'],
            tokens_used=task_info['tokens'],
            cost=task_info['cost'],
            iterations=task_info['iterations'],
            error_message=task_info.get('error'),
            code_quality_score=task_info['quality'],
            test_pass_rate=task_info['test_rate']
        )
        
        # 模拟用户反馈（成功的任务才有反馈）
        if task_info['success']:
            satisfaction = 3.5 + (task_info['quality'] * 1.5)  # 基于质量计算满意度
            collector.record_feedback(
                task_id=task_info['task_id'],
                satisfaction_score=min(5.0, satisfaction),
                feedback_text=f"Good quality code, {task_info['iterations']} iterations",
                would_recommend=task_info['quality'] > 0.8
            )
        
        print(f"   ✅ 完成 (耗时: {task_info['duration']}s, 质量: {task_info['quality']})")
    
    print()
    
    # 3. 拍摄能力快照
    print("[3/5] 拍摄能力快照...")
    snapshot = collector.take_capability_snapshot()
    print(f"✅ 能力快照已生成")
    print(f"   综合评分: {snapshot.overall_score}")
    print(f"   成功率: {snapshot.success_rate}%")
    print(f"   效率: {snapshot.efficiency_gain}%")
    print(f"   满意度: {snapshot.user_satisfaction}%")
    print()
    
    # 4. 导出数据为 JSON（可选）
    print("[4/5] 导出数据...")
    json_file = collector.export_to_json("openhands_demo_data.json")
    print()
    
    # 5. 提交到 SOHH 数据库
    print("[5/5] 提交数据到 SOHH...")
    result = collector.submit_to_sohh(db_path="data/holo_half.db")
    print()
    
    if result['success']:
        print("="*70)
        print("✅ 集成演示完成！")
        print("="*70)
        print()
        print("📊 数据统计:")
        print(f"   任务记录: {result['tasks_inserted']}")
        print(f"   用户反馈: {result['feedbacks_inserted']}")
        print(f"   能力快照: {result['snapshots_inserted']}")
        print()
        print("💡 下一步:")
        print("   1. 运行 python simple_gen.py 生成可视化报告")
        print("   2. 查看 reports/ 目录中的 HTML 报告")
        print("   3. 将此集成代码应用到真实的 OpenHands 项目中")
    else:
        print(f"❌ 提交失败: {result.get('error')}")


def integration_guide():
    """
    打印集成指南
    """
    guide = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   📖 OpenHands + SOHH 集成指南                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

🎯 集成步骤:

1️⃣  安装 SOHH 标准接口
    pip install sohh-standard-interface
   
   或者直接复制 sohh_standard_interface.py 到你的项目

2️⃣  在 OpenHands 初始化时创建采集器
    from sohh_standard_interface import create_collector
    
    collector = create_collector(
        agent_id="openhands-v1.0",
        project_id="your-project-id"
    )

3️⃣  在任务执行流程中插入采集点

    # 任务开始时
    collector.start_task(
        task_id=task.id,
        description=task.description,
        metadata={"framework": task.framework}
    )
    
    # 任务执行中 - 记录技能使用
    collector.record_skill_usage(
        skill_id="code_gen",
        skill_name="Code Generation",
        task_id=task.id,
        success=True,
        duration=execution_time
    )
    
    # 任务结束时
    collector.end_task(
        task_id=task.id,
        success=result.success,
        tokens_used=result.tokens,
        cost=result.cost,
        iterations=result.iterations,
        code_quality_score=quality_score,
        test_pass_rate=test_rate
    )
    
    # 收集用户反馈
    collector.record_feedback(
        task_id=task.id,
        satisfaction_score=user_rating,
        feedback_text=user_comment
    )

4️⃣  定期提交数据
    # 每完成一个任务后
    collector.submit_to_sohh(db_path="data/holo_half.db")
    
    # 或者批量提交
    collector.take_capability_snapshot()  # 拍摄能力快照
    collector.submit_to_sohh()

5️⃣  生成报告
    cd Self_Optimizing_Holo_Half
    python simple_gen.py

📊 数据流向:

    OpenHands 执行任务
         ↓
    SOHHDataCollector 采集数据
         ↓
    SQLite 数据库 (holo_half.db)
         ↓
    VisualizationReportGenerator 生成报告
         ↓
    HTML/Markdown 报告

🔗 标准接口优势:

✅ 松耦合 - OpenHands 无需依赖 SOHH 内部实现
✅ 标准化 - 统一的六维评估体系
✅ 可扩展 - 支持自定义字段和元数据
✅ 兼容性 - 未来版本向后兼容
✅ 生态化 - 其他 Agent 系统也可接入

🌟 生态系统愿景:

    定义标准 → SOHH 参考实现 → 其他项目接入 → 统一评估生态
    
    就像 USB 接口一样，一旦标准确立，整个生态都会跟随！

📚 更多信息:
    - 标准接口文档: sohh_standard_interface.py
    - 集成示例: openhands_integration_example.py
    - 报告生成: simple_gen.py

    """
    print(guide)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--guide":
        integration_guide()
    else:
        simulate_openhands_task_execution()
