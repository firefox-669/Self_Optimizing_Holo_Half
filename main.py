"""
Self_Optimizing_Holo_Half 主入口

Usage:
    python main.py [--mode normal|evolution] [--config config.yaml]
"""

import asyncio
import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Self_Optimizing_Holo_Half - AI Agent Self-Evolution Platform"
    )
    parser.add_argument(
        "--mode",
        choices=["normal", "evolution"],
        default="normal",
        help="运行模式: normal (生产) 或 evolution (进化)"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="配置文件路径"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="运行快速测试"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="启动自动进化调度器（每天自动执行）"
    )
    
    args = parser.parse_args()
    
    if args.test:
        # 运行快速测试
        print("🧪 Running quick tests...")
        from quick_test import run_all_tests
        success = run_all_tests()
        sys.exit(0 if success else 1)
    
    # 初始化数据库
    print("📦 Initializing database...")
    from user_scoring.database import init_db
    init_db()
    
    # 加载配置
    print(f"⚙️  Loading configuration from {args.config}...")
    try:
        import yaml
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"⚠️  Config file {args.config} not found, using defaults")
        config = {}
    
    # 设置模式
    mode = args.mode or config.get('mode', 'normal')
    print(f"🚀 Starting in '{mode}' mode")
    
    # 初始化引擎
    print("🔧 Initializing engine...")
    try:
        from core.engine import SelfOptimizingEngine
        
        async with SelfOptimizingEngine(workspace=".") as engine:
            print("✅ Engine initialized successfully!\n")
            
            if mode == "evolution":
                print("="*60)
                print("🔄 Running Self-Evolution Cycle")
                print("="*60)
                
                # 运行进化循环
                result = await engine.run_self_evolution_cycle()
                
                print("\n📊 Evolution Results:")
                print(f"   Status: {result.get('status', 'unknown')}")
                if result.get('analysis'):
                    print(f"   Analysis completed: ✅")
                if result.get('suggestions'):
                    print(f"   Suggestions generated: {len(result['suggestions'])}")
                if result.get('applied'):
                    print(f"   Optimizations applied: {len(result['applied'])}")
            
            elif args.auto:
                print("="*60)
                print("⚙️  Starting Auto-Evolution Scheduler")
                print("="*60)
                print("\n📅 The system will automatically run every day at 02:00")
                print("🔄 Each cycle does 3 things:")
                print("   1. 📰 Fetch latest information (GitHub, RSS)")
                print("   2. 🧠 Analyze with LLM")
                print("   3. 📊 Make decisions (A/B test + 6-dim scoring)")
                print("\n⏳ Running in background... Press Ctrl+C to stop\n")
                
                from core.auto_scheduler import AutoEvolutionScheduler
                scheduler = AutoEvolutionScheduler(engine=engine)
                await scheduler.start()
                
            else:
                print("="*60)
                print("✨ Normal Mode - Ready for Tasks")
                print("="*60)
                print("\n💡 Example usage:")
                print("   result = await engine.execute('Your task here')")
                print("   print(result)")
                
                # 保持运行，等待用户交互
                print("\n⏳  Press Ctrl+C to exit...\n")
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
    
    except ImportError as e:
        print(f"❌ Failed to import engine: {e}")
        print("\n💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
