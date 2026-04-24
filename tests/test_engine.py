
   """
测试 core/engine.py 是否可以正常导入和初始化
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


def test_engine_imports():
    """测试引擎的所有导入"""
    print("🧪 Testing engine.py imports...\n")
    
    try:
        print("1. Testing executor.executor...")
        from executor.executor import OpenHandsExecutor
        print("   ✅ OpenHandsExecutor imported")
        
        print("\n2. Testing evolution.evolver...")
        from evolution.evolver import EvoEngine
        print("   ✅ EvoEngine imported")
        
        print("\n3. Testing monitor.safety...")
        from monitor.safety import SafetyMonitor
        print("   ✅ SafetyMonitor imported")
        
        print("\n4. Testing patches.fixes...")
        from patches.fixes import PatchManager
        print("   ✅ PatchManager imported")
        
        print("\n5. Testing ai_news.integrator...")
        from ai_news.integrator import NewsIntegrator
        print("   ✅ NewsIntegrator imported")
        
        print("\n6. Testing evaluation.evaluator...")
        from evaluation.evaluator import CapabilityEvaluator
        print("   ✅ CapabilityEvaluator imported")
        
        print("\n7. Testing integrations...")
        from integrations.openhands import OpenHandsClient
        from integrations.openspace import OpenSpaceClient
        print("   ✅ OpenHandsClient imported")
        print("   ✅ OpenSpaceClient imported")
        
        print("\n8. Testing analyzer...")
        from analyzer import (
            OpenHandsAnalyzer,
            OpenSpaceAnalyzer,
            ProjectSelfAnalyzer,
            InfoCollector,
        )
        print("   ✅ All analyzers imported")
        
        print("\n9. Testing evolution.suggestion_engine...")
        from evolution.suggestion_engine import EvolutionSuggestionEngine
        print("   ✅ EvolutionSuggestionEngine imported")
        
        print("\n10. Testing version_control...")
        from version_control import SnapshotManager, ChangeLogger, RollbackManager
        print("   ✅ Version control modules imported")
        
        print("\n11. Testing optimizer...")
        from optimizer import AutoOptimizer, EffectEvaluator
        print("   ✅ Optimizer modules imported")
        
        print("\n12. Testing reporting...")
        from reporting import DailyReportGenerator, DeepAnalyzer
        print("   ✅ Reporting modules imported")
        
        print("\n13. Testing core.evolution_loop...")
        from core.evolution_loop import SelfEvolutionLoop
        print("   ✅ SelfEvolutionLoop imported")
        
        print("\n" + "="*70)
        print("✅ ALL IMPORTS SUCCESSFUL!")
        print("="*70)
        return True
        
    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_engine_initialization():
    """测试引擎初始化（不需要外部服务）"""
    print("\n🧪 Testing engine initialization...\n")
    
    try:
        from core.engine import SelfOptimizingEngine
        import tempfile
        
        # 使用临时目录测试
        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"Creating engine in temporary directory: {tmpdir}")
            
            # 禁用需要外部服务的组件
            engine = SelfOptimizingEngine(
                workspace=tmpdir,
                openhands_url="http://localhost:3000",  # 不会实际连接
                enable_evolution=False,  # 禁用 OpenSpace
                enable_safety_monitor=True,
                enable_ai_news=False,  # 禁用新闻
                enable_self_evolution=False,  # 禁用自我进化循环
            )
            
            print("✅ Engine initialized successfully!")
            print(f"   - Executor: {type(engine.executor).__name__}")
            print(f"   - Safety Monitor: {type(engine.safety_monitor).__name__}")
            print(f"   - Patch Manager: {type(engine.patch_manager).__name__}")
            print(f"   - Evaluator: {type(engine.evaluator).__name__}")
            
        return True
        
    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*70)
    print("Testing core/engine.py - Complete Verification")
    print("="*70)
    print()
    
    # 测试 1: 导入
    import_success = test_engine_imports()
    
    # 测试 2: 初始化
    if import_success:
        init_success = test_engine_initialization()
    else:
        init_success = False
    
    print("\n" + "="*70)
    if import_success and init_success:
        print("✅ ALL TESTS PASSED - engine.py is fully functional!")
    else:
        print("❌ SOME TESTS FAILED - see errors above")
    print("="*70)
    
    sys.exit(0 if (import_success and init_success) else 1)
