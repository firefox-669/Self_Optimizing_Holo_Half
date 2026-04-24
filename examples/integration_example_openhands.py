"""
OpenHands 集成 SOHH 标准示例

本脚本演示了如何将 SOHH 评估系统集成到 OpenHands (或任何 AI Agent 项目) 中。
它遵循"USB 接口"设计理念：松耦合、标准化、非侵入式。

集成步骤：
1. 初始化 SOHHDataCollector (数据采集器)
2. 在任务生命周期中记录关键事件 (Start/End/Feedback)
3. 定期提交数据并获取进化建议 (Suggestion Engine)
"""
import sys
import os
# 确保能导入父目录的 SOHH 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
from datetime import datetime
from sohh_standard_interface import SOHHDataCollector, create_collector
from suggestion_engine import SOHHSuggestionEngine


class OpenHandsSOHHIntegration:
    """
    OpenHands 的 SOHH 集成助手类
    
    在实际项目中，你可以将这个类封装到 OpenHands 的核心执行引擎中。
    """
    
    def __init__(self, agent_version="openhands-v1.0", project_id="demo-project"):
        # 1. 初始化数据采集器 (Input Interface)
        self.collector = create_collector(agent_id=agent_version, project_id=project_id)
        
        # 2. 初始化建议引擎 (Output Interface)
        self.suggestion_engine = SOHHSuggestionEngine()
        
        print(f"✅ SOHH 集成已就绪: {agent_version}")

    def execute_task(self, task_description: str):
        """模拟执行一个 Agent 任务"""
        task_id = f"task_{int(time.time())}_{random.randint(1000, 9999)}"
        
        print(f"\n🚀 开始执行任务: {task_description}")
        
        # --- 核心集成点 1: 记录任务开始 ---
        self.collector.start_task(
            task_id=task_id,
            description=task_description,
            metadata={"model": "gpt-4o", "temperature": 0.7}
        )
        
        # 模拟任务执行过程...
        time.sleep(random.uniform(1, 3))
        
        # 模拟执行结果
        success = random.random() > 0.2  # 80% 成功率
        tokens = random.randint(500, 2000)
        cost = tokens * 0.00001
        
        print(f"   {'✅ 成功' if success else '❌ 失败'} | Tokens: {tokens} | Cost: ${cost:.4f}")
        
        # --- 核心集成点 2: 记录任务结束 ---
        self.collector.end_task(
            task_id=task_id,
            success=success,
            tokens_used=tokens,
            cost=cost,
            iterations=random.randint(1, 5),
            code_quality_score=random.uniform(0.6, 0.95) if success else None
        )
        
        # --- 核心集成点 3: 记录用户反馈 (可选) ---
        if success:
            satisfaction = random.uniform(3.5, 5.0)
            self.collector.record_feedback(
                task_id=task_id,
                satisfaction_score=satisfaction,
                feedback_text="代码质量不错，但速度可以更快"
            )

    def sync_and_get_advice(self):
        """同步数据到 SOHH 数据库并获取进化建议"""
        print("\n" + "="*50)
        print("🔄 正在同步数据到 SOHH 数据库...")
        
        # --- 核心集成点 4: 提交数据 ---
        # 在实际项目中，这可以是一个后台定时任务
        self.collector.submit_to_sohh(db_path="data/holo_half.db")
        
        # --- 核心集成点 5: 获取进化建议 ---
        print("💡 正在从 SOHH 获取进化建议...")
        report = self.suggestion_engine.get_evolution_suggestions(
            agent_id=self.collector.agent_id
        )
        
        # 打印标准化的 JSON 报告
        print(f"\n📊 进化建议报告 (JSON格式):")
        print(report.to_json())
        
        return report


def main():
    """
    主函数：演示完整的集成工作流
    """
    # 实例化集成助手
    integration = OpenHandsSOHHIntegration()
    
    # 模拟运行几个任务以产生数据
    tasks = [
        "修复 Python 脚本中的内存泄漏问题",
        "为 Flask API 编写单元测试",
        "重构 legacy_code.py 以提高可读性",
        "部署应用到 AWS Lambda",
        "分析服务器日志并找出异常原因"
    ]
    
    for task in tasks:
        integration.execute_task(task)
        time.sleep(0.5)
    
    # 拍摄能力快照并获取建议
    integration.collector.take_capability_snapshot()
    integration.sync_and_get_advice()


if __name__ == "__main__":
    main()
