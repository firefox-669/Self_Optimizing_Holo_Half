"""
AutoGen 集成示例

展示如何使用 SOHH 评估 AutoGen Agent 的性能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from plugins.autogen_analyzer import AutoGenAnalyzer
from sohh_standard_interface import create_collector


def simulate_autogen_chat_log():
    """模拟生成 AutoGen 的对话日志"""
    
    # 创建模拟的 AutoGen GroupChat 消息
    messages = [
        {
            "name": "user",
            "content": "帮我写一个Python函数来计算斐波那契数列",
            "timestamp": 1714032000
        },
        {
            "name": "assistant",
            "content": "好的，我来帮你写一个斐波那契数列函数。\n\n```python\ndef fibonacci(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    \n    fib = [0, 1]\n    for i in range(2, n):\n        fib.append(fib[i-1] + fib[i-2])\n    return fib\n```\n\n这个函数可以计算前n个斐波那契数。",
            "timestamp": 1714032015
        },
        {
            "name": "user",
            "content": "能优化一下吗？用递归的方式",
            "timestamp": 1714032030
        },
        {
            "name": "assistant",
            "content": "当然可以！这是递归版本：\n\n```python\ndef fibonacci_recursive(n, memo={}):\n    if n in memo:\n        return memo[n]\n    if n <= 0:\n        return []\n    if n == 1:\n        return [0]\n    if n == 2:\n        return [0, 1]\n    \n    result = fibonacci_recursive(n-1, memo)\n    result.append(result[-1] + result[-2])\n    memo[n] = result\n    return result\n```\n\n这个版本使用了记忆化技术来提高效率。",
            "timestamp": 1714032050
        },
        {
            "name": "critic",
            "content": "代码看起来不错，但有几个建议：\n1. 可变默认参数可能导致意外行为\n2. 可以添加类型注解\n3. 建议添加文档字符串",
            "timestamp": 1714032065
        },
        {
            "name": "assistant",
            "content": "谢谢反馈！这是改进后的版本：\n\n```python\nfrom typing import List\n\ndef fibonacci_recursive(n: int, memo: dict = None) -> List[int]:\n    \"\"\"\n    使用递归和记忆化计算斐波那契数列\n    \n    Args:\n        n: 要计算的斐波那契数的个数\n        memo: 记忆化字典\n        \n    Returns:\n        斐波那契数列列表\n    \"\"\"\n    if memo is None:\n        memo = {}\n    \n    if n in memo:\n        return memo[n]\n    if n <= 0:\n        return []\n    if n == 1:\n        return [0]\n    if n == 2:\n        return [0, 1]\n    \n    result = fibonacci_recursive(n-1, memo)\n    result.append(result[-1] + result[-2])\n    memo[n] = result\n    return result\n```\n\n现在代码更加健壮和易读了！",
            "timestamp": 1714032085
        }
    ]
    
    # 保存为 JSON 文件
    log_dir = Path("data/autogen_demo")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "chat_log.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已生成 AutoGen 对话日志: {log_file}")
    return log_file


def analyze_autogen_performance():
    """分析 AutoGen Agent 的性能"""
    
    print("="*70)
    print("🔍 AutoGen 性能分析演示")
    print("="*70)
    
    # 1. 生成模拟日志
    log_file = simulate_autogen_chat_log()
    
    # 2. 使用 AutoGenAnalyzer 解析日志
    print("\n📊 步骤 1: 解析 AutoGen 日志")
    analyzer = AutoGenAnalyzer()
    
    if not analyzer.is_compatible(str(log_file)):
        print("❌ 日志格式不兼容")
        return
    
    steps = analyzer.collect_trace(str(log_file))
    print(f"\n✅ 成功提取 {len(steps)} 个执行步骤")
    
    # 3. 分析指标
    print("\n📊 步骤 2: 计算性能指标")
    metrics = analyzer.analyze_metrics(steps)
    
    print(f"\n框架: {metrics['framework']}")
    print(f"总步骤数: {metrics['total_steps']}")
    print(f"用户输入: {metrics['user_inputs']}")
    print(f"Agent思考: {metrics['agent_thoughts']}")
    print(f"工具调用: {metrics['tool_calls']}")
    print(f"参与Agent数: {metrics['unique_agents']}")
    print(f"Agent列表: {', '.join(metrics['agent_list'])}")
    print(f"多Agent协作: {'是' if metrics['is_multi_agent'] else '否'}")
    
    # 4. 使用标准接口采集数据
    print("\n📊 步骤 3: 使用 SOHH 标准接口")
    collector = create_collector(
        agent_id="autogen-demo",
        project_id="fibonacci-task"
    )
    
    # 记录任务开始
    task_id = "autogen-task-001"
    collector.start_task(
        task_id=task_id,
        description="Generate optimized Fibonacci function with code review",
        metadata={"framework": "AutoGen", "task_type": "code_generation"}
    )
    
    # 模拟任务执行结果
    collector.end_task(
        task_id=task_id,
        success=True,
        iterations=len(steps),
        tokens_used=2500,
        cost=0.012,
        code_quality_score=0.92,
        test_pass_rate=1.0
    )
    
    # 记录用户反馈
    collector.record_feedback(
        task_id=task_id,
        satisfaction_score=4.5,
        feedback_text="Excellent code quality with good optimization and documentation"
    )
    
    # 拍摄能力快照
    snapshot = collector.take_capability_snapshot()
    
    print(f"\n✅ 能力快照:")
    print(f"   综合评分: {snapshot.overall_score:.2f}")
    print(f"   成功率: {snapshot.success_rate:.2f}")
    print(f"   效率: {snapshot.efficiency_gain:.2f}")
    print(f"   满意度: {snapshot.user_satisfaction:.2f}")
    
    # 5. 提交到数据库
    print("\n📊 步骤 4: 提交数据到 SOHH")
    result = collector.submit_to_sohh(db_path="data/holo_half.db")
    
    if result:
        print("✅ 数据提交成功！")
    else:
        print("❌ 数据提交失败")
    
    print("\n" + "="*70)
    print("🎉 AutoGen 性能分析完成！")
    print("="*70)
    print("\n💡 提示: 运行 python simple_gen.py 生成可视化报告")


if __name__ == "__main__":
    analyze_autogen_performance()
