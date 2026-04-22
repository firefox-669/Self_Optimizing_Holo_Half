#!/usr/bin/env python3
"""
快速测试脚本

验证所有核心模块是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_database():
    """测试数据库初始化"""
    print("=" * 60)
    print("Testing Database Initialization...")
    print("=" * 60)
    
    try:
        from user_scoring.database import init_db
        init_db(":memory:")  # 使用内存数据库测试
        print("✅ Database initialization: PASSED\n")
        return True
    except Exception as e:
        print(f"❌ Database initialization: FAILED - {e}\n")
        return False


def test_behavior_tracker():
    """测试行为追踪器"""
    print("=" * 60)
    print("Testing Behavior Tracker...")
    print("=" * 60)
    
    try:
        from user_scoring.behavior_tracker import UserBehaviorTracker
        
        tracker = UserBehaviorTracker(":memory:")
        
        # 记录任务执行
        task_id = tracker.record_task_execution({
            "user_id": "test_user",
            "mode": "normal",
            "task_type": "openhands",
            "instruction": "Test task",
            "status": "success",
            "duration_seconds": 45.2,
            "tokens_used": 1234
        })
        
        # 记录反馈
        tracker.record_user_feedback(task_id, rating=5)
        
        # 获取指标
        metrics = tracker.get_task_metrics(task_id)
        
        if metrics and metrics["status"] == "success":
            print("✅ Behavior tracker: PASSED\n")
            tracker.close()
            return True
        else:
            print("❌ Behavior tracker: FAILED - Invalid metrics\n")
            tracker.close()
            return False
            
    except Exception as e:
        print(f"❌ Behavior tracker: FAILED - {e}\n")
        return False


def test_scoring_engine():
    """测试评分引擎"""
    print("=" * 60)
    print("Testing Scoring Engine...")
    print("=" * 60)
    
    try:
        from evolution_engine.evaluator.scoring_engine import ComprehensiveScoringSystem
        
        scorer = ComprehensiveScoringSystem()
        
        # 模拟数据
        version_metrics = {
            "total_tasks": 100,
            "success_count": 92,
            "fail_count": 8,
            "avg_duration": 38.5,
            "avg_tokens": 1150,
            "avg_rating": 4.6,
            "unique_users": 30,
            "days_since_last_use": 1,
            "total_tokens": 115000,
            "success_rate": 0.92,
            "reuse_rate": 0.75,
            "implicit_feedback_avg": 4.3,
            "is_new_feature": True,
            "tech_tags": ["ai", "automation"],
            "fills_capability_gap": True
        }
        
        baseline_metrics = {
            "total_tasks": 80,
            "avg_duration": 45.2,
            "avg_tokens": 1350,
            "avg_rating": 4.2
        }
        
        result = scorer.calculate_comprehensive_score(
            "test_skill",
            version_metrics,
            baseline_metrics
        )
        
        if result["overall_score"] > 0 and result["recommendation"]:
            print(f"   Overall Score: {result['overall_score']}")
            print(f"   Grade: {result['grade']}")
            print(f"   Recommendation: {result['recommendation']}")
            print("✅ Scoring engine: PASSED\n")
            return True
        else:
            print("❌ Scoring engine: FAILED - Invalid result\n")
            return False
            
    except Exception as e:
        print(f"❌ Scoring engine: FAILED - {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_ab_test_framework():
    """测试 A/B 测试框架"""
    print("=" * 60)
    print("Testing A/B Test Framework...")
    print("=" * 60)
    
    try:
        from evolution_engine.optimizer.ab_test_framework import ABTestFramework
        import asyncio
        
        async def run_test():
            framework = ABTestFramework(":memory:")
            
            # 启动测试
            config = await framework.start_ab_test(
                test_id="test_001",
                version_a="v1.0",
                version_b="v2.0",
                duration_days=7
            )
            
            # 模拟用户分配
            for i in range(10):
                variant = await framework.route_request(f"user_{i}", "test_001")
            
            framework.close()
            return True
        
        result = asyncio.run(run_test())
        
        if result:
            print("✅ A/B test framework: PASSED\n")
            return True
        else:
            print("❌ A/B test framework: FAILED\n")
            return False
            
    except Exception as e:
        print(f"❌ A/B test framework: FAILED - {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_mode_manager():
    """测试模式管理器"""
    print("=" * 60)
    print("Testing Mode Manager...")
    print("=" * 60)
    
    try:
        from mode_management.mode_manager import ModeManager
        
        manager = ModeManager()
        
        # 测试模式切换
        current = manager.get_current_mode()
        manager.set_mode("evolution")
        
        if manager.is_evolution_mode():
            manager.set_mode("normal")
            print(f"   Current mode: {manager.get_current_mode()}")
            print("✅ Mode manager: PASSED\n")
            return True
        else:
            print("❌ Mode manager: FAILED - Mode switch failed\n")
            return False
            
    except Exception as e:
        print(f"❌ Mode manager: FAILED - {e}\n")
        return False


def test_analyzers():
    """测试分析器"""
    print("=" * 60)
    print("Testing Analyzers...")
    print("=" * 60)
    
    try:
        from integrations.openhands.capability_analyzer import CapabilityAnalyzer
        from integrations.openhands.gap_detector import GapDetector
        from integrations.openspace.skill_analyzer import SkillAnalyzer
        from integrations.openhands.performance_monitor import PerformanceMonitor
        
        # 实例化（不需要实际客户端）
        gap_detector = GapDetector()
        perf_monitor = PerformanceMonitor()
        
        # 测试性能监控
        perf_monitor.record_execution({
            "task_id": "test_001",
            "duration_seconds": 45.2,
            "tokens_used": 1234,
            "status": "success"
        })
        
        metrics = perf_monitor.get_current_metrics(30)
        
        if metrics["total_executions"] > 0:
            print("✅ Analyzers: PASSED\n")
            return True
        else:
            print("❌ Analyzers: FAILED\n")
            return False
            
    except Exception as e:
        print(f"❌ Analyzers: FAILED - {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Self_Optimizing_Holo_Half - Quick Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        ("Database", test_database),
        ("Behavior Tracker", test_behavior_tracker),
        ("Scoring Engine", test_scoring_engine),
        ("A/B Test Framework", test_ab_test_framework),
        ("Mode Manager", test_mode_manager),
        ("Analyzers", test_analyzers),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ {name}: EXCEPTION - {e}\n")
            results.append((name, False))
    
    # 总结
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:30s} {status}")
    
    print("-" * 60)
    print(f"Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Ready for GitHub release!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Please fix before release.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
