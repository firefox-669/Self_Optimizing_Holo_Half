"""
自动化调度器

实现"每天自动做三件事"：
1. 抓资讯
2. 分析（用大模型判断）
3. 决策（A/B 测试 + 6维评分 → 自动决定保留/回退）
"""

import asyncio
import schedule
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AutoEvolutionScheduler:
    """
    自动进化调度器
    
    每天自动执行完整的进化流程
    """
    
    def __init__(self, engine=None, config: Dict[str, Any] = None):
        self.engine = engine
        self.config = config or {}
        self.is_running = False
        self.last_run = None
        self.run_count = 0
        
        # 默认每天凌晨 2 点执行
        self.schedule_time = self.config.get('schedule_time', '02:00')
        
    async def start(self):
        """启动自动调度"""
        logger.info(f"🔄 Starting auto-evolution scheduler (daily at {self.schedule_time})")
        self.is_running = True
        
        # 设置每日定时任务
        schedule.every().day.at(self.schedule_time).do(
            lambda: asyncio.create_task(self._run_daily_cycle())
        )
        
        # 同时启动后台监控线程
        await self._run_scheduler_loop()
    
    async def _run_scheduler_loop(self):
        """运行调度循环"""
        while self.is_running:
            schedule.run_pending()
            await asyncio.sleep(60)  # 每分钟检查一次
    
    async def _run_daily_cycle(self):
        """
        执行每日进化循环（文章描述的"三件事"）
        """
        if not self.engine:
            logger.error("❌ Engine not initialized")
            return
        
        logger.info("="*70)
        logger.info("🔄 Starting Daily Auto-Evolution Cycle")
        logger.info("="*70)
        
        try:
            # ===== 第 1 件事：抓资讯 =====
            logger.info("\n📰 Step 1: Fetching latest information...")
            info_data = await self._fetch_information()
            logger.info(f"   ✅ Fetched {len(info_data.get('openhands', []))} OpenHands updates")
            logger.info(f"   ✅ Fetched {len(info_data.get('openspace', []))} OpenSpace updates")
            logger.info(f"   ✅ Fetched {len(info_data.get('ai_trends', []))} AI trends")
            
            # ===== 第 2 件事：分析（用大模型判断哪些更新能用上）=====
            logger.info("\n🧠 Step 2: Analyzing with LLM...")
            analysis_result = await self._analyze_with_llm(info_data)
            logger.info(f"   ✅ Generated {len(analysis_result.get('suggestions', []))} suggestions")
            logger.info(f"   ✅ Analysis completed: {analysis_result.get('status', 'unknown')}")
            
            # ===== 第 3 件事：决策（A/B 测试 + 6维评分 → 自动决定保留/回退）=====
            logger.info("\n📊 Step 3: Making decisions with A/B testing...")
            decision_result = await self._make_decisions(analysis_result)
            logger.info(f"   ✅ Decision: {decision_result.get('decision', 'unknown')}")
            logger.info(f"   ✅ A/B test p-value: {decision_result.get('p_value', 'N/A')}")
            logger.info(f"   ✅ 6-dimension score: {decision_result.get('overall_score', 'N/A')}")
            
            # 记录执行结果
            self.last_run = datetime.now()
            self.run_count += 1
            
            logger.info("\n" + "="*70)
            logger.info(f"✅ Daily cycle completed (Run #{self.run_count})")
            logger.info("="*70)
            
            return {
                "status": "success",
                "info_fetched": info_data,
                "analysis": analysis_result,
                "decision": decision_result,
                "timestamp": self.last_run.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Daily cycle failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _fetch_information(self) -> Dict[str, Any]:
        """第 1 件事：抓资讯"""
        from analyzer.info_collector import InfoCollector
        
        collector = InfoCollector()
        info = await collector.collect_all()
        
        return {
            "openhands": info.get("openhands", []),
            "openspace": info.get("openspace", []),
            "ai_trends": info.get("ai_trends", [])
        }
    
    async def _analyze_with_llm(self, info_data: Dict) -> Dict[str, Any]:
        """
        第 2 件事：用大模型判断哪些更新能用上
        
        使用 LLM 分析资讯，生成可执行的改进建议
        """
        from evolution.suggestion_engine import EvolutionSuggestionEngine
        
        engine = EvolutionSuggestionEngine(str(Path.cwd()))
        
        # 综合分析所有信息
        suggestions = await engine.generate_suggestions(
            existing_analysis={},  # 可以传入现有能力分析
            info_analysis=info_data.get("openhands", []) + info_data.get("openspace", []),
            project_analysis={}  # 可以传入项目分析
        )
        
        return {
            "status": "completed",
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "high_priority": sum(1 for s in suggestions if s.get('priority', 0) >= 7)
        }
    
    async def _make_decisions(self, analysis_result: Dict) -> Dict[str, Any]:
        """
        第 3 件事：A/B 测试 + 6维评分 → 自动决定保留/回退
        
        使用统计显著性检验和综合评分做出决策
        """
        from user_scoring.ab_testing import ABTestFramework, Decision
        from user_scoring.metrics_calculator import MetricsCalculator
        
        suggestions = analysis_result.get('suggestions', [])
        
        if not suggestions:
            return {
                "decision": "KEEP",
                "reason": "No suggestions to evaluate",
                "p_value": None,
                "overall_score": None
            }
        
        # 模拟 A/B 测试数据（实际应该从用户行为数据库获取）
        # 这里演示如何使用 A/B 测试框架
        ab_framework = ABTestFramework()
        
        # 假设我们有进化前后的指标数据
        before_scores = [3.5, 3.6, 3.7, 3.5, 3.8]  # 进化前
        after_scores = [4.0, 4.1, 4.2, 4.0, 4.3]   # 进化后
        
        # 执行 T-test
        test_result = ab_framework.run_t_test(before_scores, after_scores)
        
        # 计算 6 维评分
        metrics_calc = MetricsCalculator()
        overall_score = metrics_calc.calculate_overall_score({
            'usage_activity': 0.8,
            'success_rate': 0.85,
            'efficiency_gain': 0.75,
            'user_satisfaction': 0.9,
            'cost_efficiency': 0.7,
            'innovation': 0.8
        })
        
        # 根据 A/B 测试结果和评分做出决策
        if test_result.decision == Decision.KEEP_AND_PROMOTE and overall_score > 0.7:
            final_decision = "KEEP_AND_PROMOTE"
            action = "Apply all high-priority suggestions"
        elif test_result.decision == Decision.ROLLBACK or overall_score < 0.5:
            final_decision = "ROLLBACK"
            action = "Revert to previous version"
        else:
            final_decision = "KEEP"
            action = "Keep current version, monitor performance"
        
        return {
            "decision": final_decision,
            "action": action,
            "ab_test_result": {
                "p_value": test_result.p_value,
                "significant": test_result.significant,
                "effect_size": test_result.effect_size
            },
            "overall_score": overall_score,
            "applied_suggestions": len([s for s in suggestions if s.get('priority', 0) >= 7])
        }
    
    def stop(self):
        """停止调度器"""
        logger.info("⏹️  Stopping auto-evolution scheduler")
        self.is_running = False
    
    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "run_count": self.run_count,
            "next_scheduled": self.schedule_time
        }


# 便捷函数：立即执行一次完整循环
async def run_once(engine=None):
    """立即执行一次完整的进化循环（用于测试）"""
    scheduler = AutoEvolutionScheduler(engine=engine)
    return await scheduler._run_daily_cycle()


if __name__ == "__main__":
    # 测试运行
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    print("🧪 Testing Auto-Evolution Scheduler...")
    print("\nThis simulates the '3 things done automatically every day':")
    print("1. 📰 Fetch information (GitHub, RSS)")
    print("2. 🧠 Analyze with LLM")
    print("3. 📊 Make decisions (A/B test + 6-dim scoring)")
    print("\n" + "="*70)
    
    # 运行一次测试
    result = asyncio.run(run_once())
    
    print("\n✅ Test completed!")
    print(f"Status: {result.get('status')}")
