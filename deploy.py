#!/usr/bin/env python3
# Self_Optimizing_Holo_Half Deploy Script

import os
import sys
import subprocess
import asyncio
from pathlib import Path


def step(name, func):
    print(f"\n[{name}]")
    try:
        result = func()
        print(f"  OK" if result else "  SKIP")
        return result
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def check_python():
    v = sys.version_info
    print(f"  Python {v.major}.{v.minor}.{v.micro}")
    return v.major >= 3 and v.minor >= 10


def install_deps():
    deps = ["aiohttp>=3.9.0", "jsonschema>=4.0.0"]
    for d in deps:
        subprocess.run(["pip", "install", d], capture_output=True)
    return True


def check_openspace():
    try:
        import openspace
        return True
    except:
        return False


def check_openhands():
    import aiohttp
    import asyncio
    async def ck():
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get("http://localhost:3000/api/status", timeout=3) as r:
                    return r.status == 200
        except:
            return False
    return asyncio.run(ck())


def check_api():
    return bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))


def test_import():
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from Self_Optimizing_Holo_Half import SelfOptimizingEngine
    return True


def health_check():
    sys.path.insert(0, str(Path(__file__).parent.parent))
    async def run():
        from Self_Optimizing_Holo_Half import SelfOptimizingEngine
        engine = SelfOptimizingEngine(str(Path.cwd()))
        result = await engine.full_self_evolution()
        await engine.shutdown()
        return result
    return asyncio.run(run())


def main():
    print("=" * 50)
    print("Self_Optimizing_Holo_Half Deploy")
    print("=" * 50)
    
    results = [
        step("Python", check_python),
        step("Install deps", install_deps),
        step("OpenSpace", check_openspace),
        step("OpenHands", check_openhands),
        step("API Key", check_api),
        step("Import", test_import),
        step("Health", health_check),
    ]
    
    print("\n" + "=" * 50)
    print("RESULT:", "OK" if all(results[:5]) else "NEED SETUP")
    print("=" * 50)
    print("\nTo use:")
    print("  1. export OPENAI_API_KEY=sk-xxx")
    print("  2. python example.py")


if __name__ == "__main__":
    main()