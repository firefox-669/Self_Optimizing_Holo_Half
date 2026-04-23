#!/usr/bin/env python3
"""
Self_Optimizing_Holo_Half 使用示例
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Self_Optimizing_Holo_Half import SelfOptimizingEngine


async def example_basic():
    """基础用法"""
    print("\n" + "=" * 50)
    print("  基础用法")
    print("=" * 50)
    
    async with SelfOptimizingEngine(
        workspace=str(Path.cwd()),
    ) as engine:
        
        # 查看连接状态
        status = engine.get_stability_report()
        print(f"\n连接状态:")
        print(f"  OpenSpace: {status['connections'].get('openspace', False)}")
        print(f"  OpenHands: {status['connections'].get('openhands', False)}")
        print(f"  稳定性: {status.get('overall_stability', 0)}")
        
        # 执行任务
        result = await engine.execute("你好，请介绍一下自己")
        print(f"\n执行结果:")
        print(f"  Success: {result.get('success')}")
        print(f"  Output: {result.get('output', '')[:200]}...")


async def example_evolve_project():
    """帮助项目进化"""
    print("\n" + "=" * 50)
    print("  帮助项目进化")
    print("=" * 50)
    
    async with SelfOptimizingEngine(
        workspace=str(Path.cwd()),
    ) as engine:
        
        # 进化openspace项目
        result = await engine.evolve_project_skills(
            str(Path(__file__).parent / "openspace")
        )
        
        print(f"\n进化结果:")
        print(f"  Success: {result.get('success')}")
        print(f"  Skills Evolved: {result.get('skills_evolved', 0)}")


async def example_learn_evolve():
    """自我学习进化"""
    print("\n" + "=" * 50)
    print("  自我学习进化")
    print("=" * 50)
    
    async with SelfOptimizingEngine(
        workspace=str(Path.cwd()),
    ) as engine:
        
        result = await engine.full_self_evolution()
        
        print(f"\n结果:")
        print(f"  Trends: {result.get('trends_count')}")
        print(f"  Improvements: {result.get('improvements_found')}")
        print(f"  Stability: {result.get('stability', {}).get('overall_stability')}")
        
        if result.get("improvements"):
            print(f"\n改进建议:")
            for imp in result["improvements"][:3]:
                print(f"  - [{imp.get('target')}] {imp.get('improvement')[:50]}")


async def main():
    print("=" * 50)
    print("  Self_Optimizing_Holo_Half 示例")
    print("=" * 50)
    
    await example_basic()
    await example_learn_evolve()
    
    print("\n" + "=" * 50)
    print("  完成")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())