"""
测试 LLM 分析功能

Usage:
    python test_llm_analysis.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


async def test_llm_client():
    """测试 LLM 客户端"""
    print("="*70)
    print("🧪 Testing LLM Client")
    print("="*70)
    
    try:
        from core.llm_client import LLMClient
        
        print("\n1️⃣  Initializing LLM client...")
        llm = LLMClient()
        print(f"   ✅ Provider: {llm.provider}")
        print(f"   ✅ Model: {llm.model}")
        
        # 模拟资讯数据
        test_info = [
            {
                "title": "OpenHands v0.15 released with improved multi-file editing",
                "source": "GitHub Release",
                "type": "version_update",
                "date": "2026-04-22",
                "url": "https://github.com/All-Hands-AI/OpenHands/releases/tag/v0.15"
            },
            {
                "title": "New skill sharing protocol in OpenSpace",
                "source": "GitHub PR",
                "type": "feature_enhancement",
                "date": "2026-04-21",
                "url": "https://github.com/HKUDS/OpenSpace/pull/123"
            }
        ]
        
        print("\n2️⃣  Calling LLM to analyze info...")
        suggestions = await llm.analyze_info(test_info)
        
        print(f"\n✅ LLM generated {len(suggestions)} suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n   Suggestion {i}:")
            print(f"   - Title: {suggestion.get('title', 'N/A')}")
            print(f"   - Target: {suggestion.get('target', 'N/A')}")
            print(f"   - Type: {suggestion.get('type', 'N/A')}")
            print(f"   - Priority: {suggestion.get('priority', 'N/A')}/10")
            print(f"   - Description: {suggestion.get('description', 'N/A')[:100]}...")
        
        if suggestions:
            print("\n✅ LLM analysis working correctly!")
            return True
        else:
            print("\n⚠️  No suggestions generated (API may have returned empty)")
            return False
    
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\n💡 Please set up your API key in .env file:")
        print("   cp .env.example .env")
        print("   # Edit .env and add your OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return False
    
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\n💡 Install required packages:")
        print("   pip install openai anthropic python-dotenv")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_suggestion_engine_with_llm():
    """测试 Suggestion Engine 使用 LLM"""
    print("\n" + "="*70)
    print("🧪 Testing Suggestion Engine with LLM")
    print("="*70)
    
    try:
        from evolution.suggestion_engine import EvolutionSuggestionEngine
        
        print("\n1️⃣  Initializing Suggestion Engine...")
        engine = EvolutionSuggestionEngine(str(Path.cwd()))
        
        # 模拟资讯数据
        test_info = [
            {
                "title": "OpenHands adds support for custom agents",
                "source": "GitHub",
                "type": "feature_enhancement",
                "date": "2026-04-22",
                "url": "https://github.com/All-Hands-AI/OpenHands"
            }
        ]
        
        print("\n2️⃣  Generating suggestions with LLM...")
        suggestions = await engine.generate_suggestions(
            existing_analysis=None,
            info_analysis=test_info,
            project_analysis=None,
            use_llm=True  # 启用 LLM
        )
        
        print(f"\n✅ Generated {len(suggestions)} suggestions")
        
        llm_suggestions = [s for s in suggestions if s.get('generated_by') == 'llm']
        rule_suggestions = [s for s in suggestions if s.get('generated_by') != 'llm']
        
        print(f"   - From LLM: {len(llm_suggestions)}")
        print(f"   - From rules: {len(rule_suggestions)}")
        
        if llm_suggestions:
            print("\n✅ LLM integration working correctly!")
            return True
        else:
            print("\n⚠️  No LLM suggestions (may have fallen back to rules)")
            return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("\n🚀 Starting LLM Analysis Tests\n")
    
    # Test 1: LLM Client
    result1 = await test_llm_client()
    
    # Test 2: Suggestion Engine with LLM
    result2 = await test_suggestion_engine_with_llm()
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    print(f"LLM Client:                    {'✅ PASSED' if result1 else '❌ FAILED'}")
    print(f"Suggestion Engine with LLM:    {'✅ PASSED' if result2 else '❌ FAILED'}")
    print("="*70)
    
    if result1 and result2:
        print("\n🎉 All tests passed! LLM analysis is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
