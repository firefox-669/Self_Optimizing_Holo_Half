"""
快速演示脚本 - 无需外部服务即可运行

展示 A/B 测试框架和评分系统的核心功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


def demo_ab_testing():
    """演示 A/B 测试功能"""
    print("\n" + "="*70)
    print("🧪 Demo: A/B Testing Framework")
    print("="*70)
    
    from user_scoring.ab_testing import ABTestFramework, Decision
    
    # 模拟进化前后的用户评分数据
    print("\n📊 Scenario: Evaluating skill evolution effect")
    print("-"*70)
    
    before_evolution = [3.5, 3.6, 3.7, 3.5, 3.8, 3.6, 3.7, 3.5]
    after_evolution = [4.0, 4.1, 4.2, 4.0, 4.3, 4.1, 4.2, 4.0]
    
    print(f"Before evolution: {before_evolution}")
    print(f"After evolution:  {after_evolution}")
    
    # 执行 T-test
    framework = ABTestFramework(significance_level=0.05)
    result = framework.run_t_test(before_evolution, after_evolution)
    
    print("\n" + framework.interpret_result(result))


def demo_scoring():
    """演示 6 维评分系统"""
    print("\n" + "="*70)
    print("📊 Demo: 6-Dimensional Scoring System")
    print("="*70)
    
    from user_scoring.metrics_calculator import MetricsCalculator
    
    calc = MetricsCalculator()
    
    # 模拟技能指标
    metrics = {
        'usage_activity': 0.85,      # 使用活跃度
        'success_rate': 0.92,        # 成功率
        'efficiency_gain': 0.78,     # 效率提升
        'user_satisfaction': 0.88,   # 用户满意度
        'cost_efficiency': 0.75,     # 成本效率
        'innovation': 0.82           # 创新性
    }
    
    print("\n📈 Skill Metrics:")
    print("-"*70)
    for dimension, score in metrics.items():
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"  {dimension:20s} [{bar}] {score:.2f}")
    
    # 计算综合评分
    overall_score = calc.calculate_overall_score(metrics)
    
    print(f"\n{'='*70}")
    print(f"Overall Score: {overall_score:.2f}/1.00")
    
    # 给出建议
    if overall_score >= 0.80:
        recommendation = "✅ KEEP_AND_PROMOTE - Excellent performance!"
    elif overall_score >= 0.65:
        recommendation = "✅ KEEP - Good performance"
    elif overall_score >= 0.50:
        recommendation = "⚠️  KEEP_WITH_IMPROVEMENT - Needs refinement"
    elif overall_score >= 0.40:
        recommendation = "🔍 REVIEW - Manual review needed"
    else:
        recommendation = "❌ ROLLBACK - Poor performance"
    
    print(f"Recommendation: {recommendation}")
    print("="*70)


def demo_version_control():
    """演示版本控制系统"""
    print("\n" + "="*70)
    print("🔄 Demo: Version Control & Rollback")
    print("="*70)
    
    from version_control.snapshot_manager import SnapshotManager
    import tempfile
    import os
    
    # 创建临时目录用于演示
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SnapshotManager(workspace=tmpdir)
        
        print("\n📝 Creating snapshots...")
        print("-"*70)
        
        # 创建快照
        snapshot1 = manager.create_snapshot("Initial version")
        print(f"✅ Snapshot 1: {snapshot1['snapshot_id'][:8]}... - Initial version")
        
        snapshot2 = manager.create_snapshot("After optimization")
        print(f"✅ Snapshot 2: {snapshot2['snapshot_id'][:8]}... - After optimization")
        
        # 列出快照
        snapshots = manager.list_snapshots()
        print(f"\n📋 Total snapshots: {len(snapshots)}")
        
        # 演示回退
        print(f"\n⏪ Rolling back to snapshot 1...")
        success = manager.rollback_to_snapshot(snapshot1['snapshot_id'])
        print(f"{'✅' if success else '❌'} Rollback {'successful' if success else 'failed'}")
    
    print("="*70)


def demo_auto_scheduler():
    """演示自动调度器概念"""
    print("\n" + "="*70)
    print("⚙️  Demo: Auto-Evolution Scheduler")
    print("="*70)
    
    print("\n📅 The auto scheduler runs every day at 02:00 AM")
    print("-"*70)
    print("\nEach cycle does 3 things automatically:")
    print("  1. 📰 Fetch latest information")
    print("     - OpenHands GitHub updates")
    print("     - OpenSpace GitHub updates")
    print("     - AI trends from RSS feeds")
    print()
    print("  2. 🧠 Analyze with LLM")
    print("     - Generate improvement suggestions")
    print("     - Prioritize by impact and feasibility")
    print()
    print("  3. 📊 Make decisions")
    print("     - A/B test new features")
    print("     - Calculate 6-dimension scores")
    print("     - Auto-decide: KEEP / PROMOTE / ROLLBACK")
    print()
    print("💡 Start auto mode: python main.py --auto")
    print("="*70)


def main():
    """主演示函数"""
    print("\n" + "🎯"*35)
    print(" Self_Optimizing_Holo_Half - Quick Demo")
    print("🎯"*35)
    print("\nThis demo shows core features WITHOUT external services.")
    print("No OpenHands or OpenSpace required!")
    
    try:
        # 运行所有演示
        demo_ab_testing()
        demo_scoring()
        demo_version_control()
        demo_auto_scheduler()
        
        print("\n" + "✨"*35)
        print(" Demo Complete!")
        print("✨"*35)
        print("\n📚 Next steps:")
        print("  1. Edit .env file with your API keys")
        print("  2. Start OpenHands service (optional)")
        print("  3. Run: python main.py --mode normal")
        print("  4. Or run: python main.py --auto (daily automation)")
        print("\n📖 See INSTALLATION_GUIDE.md for full setup instructions")
        print()
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
