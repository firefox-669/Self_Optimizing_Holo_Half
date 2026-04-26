"""
SOHH Integration Example for OpenSpace

This example demonstrates how to integrate SOHH monitoring with OpenSpace
using just a few lines of code.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def example_basic_usage():
    """
    Basic usage: Monitor OpenSpace tasks automatically
    """
    print("="*70)
    print("Example 1: Basic Usage")
    print("="*70)
    
    from openspace.tool_layer import OpenSpace, OpenSpaceConfig
    from openspace_sohh_adapter import MonitoredOpenSpace
    
    # Configure OpenSpace
    config = OpenSpaceConfig(
        llm_model="openai/minimax-m25",
        llm_kwargs={
            "base_url": os.getenv("OPENAI_BASE_URL"),
            "api_key": os.getenv("OPENAI_API_KEY")
        },
        recording_backends=["shell", "system"]
    )
    
    # Create monitored agent (just replace OpenSpace with MonitoredOpenSpace)
    agent = MonitoredOpenSpace(
        config=config,
        project_id="demo-project"
    )
    
    # Initialize
    await agent.initialize()
    
    # Execute tasks - all automatically monitored!
    tasks = [
        "Write a Python function to calculate factorial",
        "Create a simple HTML page with a button"
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n[{i}/{len(tasks)}] Executing: {task}")
        result = await agent.execute(task, max_iterations=5)
        print(f"   Status: {result.get('status')}")
        print(f"   Iterations: {result.get('iterations', 0)}")
    
    # Generate report with one line!
    print("\n📊 Generating SOHH report...")
    report_path = agent.generate_sohh_report()
    
    if report_path:
        print(f"✅ Report saved to: {report_path}")
    
    # Get statistics
    stats = agent.get_sohh_stats()
    print(f"\n📈 Statistics:")
    print(f"   Total tasks: {stats['total_tasks']}")
    print(f"   Success rate: {stats['success_rate']:.1f}%")


async def example_custom_configuration():
    """
    Advanced usage: Custom database path and project ID
    """
    print("\n" + "="*70)
    print("Example 2: Custom Configuration")
    print("="*70)
    
    from openspace.tool_layer import OpenSpace, OpenSpaceConfig
    from openspace_sohh_adapter import create_monitored_agent
    
    config = OpenSpaceConfig(
        llm_model="openai/minimax-m25",
        llm_kwargs={
            "base_url": os.getenv("OPENAI_BASE_URL"),
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    )
    
    # Use convenience function
    agent = create_monitored_agent(
        config=config,
        project_id="my-custom-project",
        db_path="data/my_project_sohh.db"
    )
    
    await agent.initialize()
    
    # Execute a task
    result = await agent.execute(
        "Write a SQL query to select users from database",
        max_iterations=5
    )
    
    print(f"Task completed: {result.get('status')}")
    
    # Generate report
    report_path = agent.generate_sohh_report()
    if report_path:
        print(f"Report: {report_path}")


async def example_comparison():
    """
    Show the difference between regular and monitored OpenSpace
    """
    print("\n" + "="*70)
    print("Example 3: Comparison - Regular vs Monitored")
    print("="*70)
    
    from openspace.tool_layer import OpenSpace, OpenSpaceConfig
    from openspace_sohh_adapter import MonitoredOpenSpace
    
    config = OpenSpaceConfig(
        llm_model="openai/minimax-m25",
        llm_kwargs={
            "base_url": os.getenv("OPENAI_BASE_URL"),
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    )
    
    print("\n❌ Regular OpenSpace (no monitoring):")
    print("   agent = OpenSpace(config=config)")
    print("   # No automatic tracking")
    print("   # Manual data collection required")
    
    print("\n✅ Monitored OpenSpace (with SOHH):")
    print("   agent = MonitoredOpenSpace(config=config)")
    print("   # ✓ Automatic task tracking")
    print("   # ✓ Zero configuration")
    print("   # ✓ One-line report generation")
    
    # Demonstrate
    agent = MonitoredOpenSpace(config=config, project_id="comparison-demo")
    await agent.initialize()
    
    result = await agent.execute("Print 'Hello World'", max_iterations=3)
    print(f"\n   Task executed: {result.get('status')}")
    
    stats = agent.get_sohh_stats()
    print(f"   Automatically tracked: {stats['total_tasks']} task(s)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SOHH Integration Examples for OpenSpace")
    print("="*70)
    
    # Run examples
    try:
        # Example 1: Basic usage
        asyncio.run(example_basic_usage())
        
        # Example 2: Custom configuration
        # asyncio.run(example_custom_configuration())
        
        # Example 3: Comparison
        asyncio.run(example_comparison())
        
        print("\n" + "="*70)
        print("✅ All examples completed!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
