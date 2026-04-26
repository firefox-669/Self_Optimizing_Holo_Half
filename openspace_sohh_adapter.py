"""
OpenSpace SOHH Adapter - Seamless Integration

This module provides a drop-in replacement for OpenSpace that automatically
monitors all task executions using SOHH (Self-Optimizing Holo-Half).

Usage:
    from openspace_sohh_adapter import MonitoredOpenSpace
    
    # Just replace OpenSpace with MonitoredOpenSpace
    agent = MonitoredOpenSpace(config=config, project_id="my-project")
    await agent.initialize()
    
    # All tasks are automatically monitored
    result = await agent.execute("Write a Python script...")
    
    # Generate report with one line
    agent.generate_sohh_report()
"""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

# Import SOHH components
from sohh_standard_interface import SOHHDataCollector


class MonitoredOpenSpace:
    """
    OpenSpace wrapper with automatic SOHH monitoring.
    
    This class wraps the original OpenSpace agent to provide seamless
    performance monitoring without modifying any existing code.
    
    Features:
    - Automatic task tracking (start/end)
    - Zero configuration required
    - Minimal overhead (< 1ms per task)
    - One-line report generation
    """
    
    def __init__(self, *args, project_id: str = "default", 
                 db_path: str = "data/openspace_sohh.db", **kwargs):
        """
        Initialize MonitoredOpenSpace.
        
        Args:
            *args: Arguments passed to OpenSpace constructor
            project_id: Project identifier for SOHH tracking
            db_path: Path to SOHH database
            **kwargs: Keyword arguments passed to OpenSpace constructor
        """
        # Import OpenSpace here to avoid circular dependencies
        from openspace.tool_layer import OpenSpace
        
        # Create the actual OpenSpace agent
        self._agent = OpenSpace(*args, **kwargs)
        
        # Initialize SOHH collector
        self._collector = SOHHDataCollector(
            agent_id="openspace",
            project_id=project_id
        )
        
        self._db_path = db_path
        self._task_counter = 0
        self._current_task_id = None
    
    async def initialize(self):
        """Initialize the underlying OpenSpace agent."""
        await self._agent.initialize()
    
    async def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task with automatic SOHH monitoring.
        
        Args:
            task: Task description
            **kwargs: Additional arguments passed to OpenSpace.execute
            
        Returns:
            Task execution result
        """
        # Generate unique task ID
        self._task_counter += 1
        task_id = f"openspace-task-{self._task_counter}"
        self._current_task_id = task_id
        
        # Start SOHH monitoring
        self._collector.start_task(
            task_id=task_id,
            description=task[:200]  # Limit description length
        )
        
        try:
            # Execute the actual task
            result = await self._agent.execute(task, **kwargs)
            
            # End SOHH monitoring
            self._collector.end_task(
                task_id=task_id,
                success=result.get('status') == 'success',
                iterations=result.get('iterations', 0),
                error_message=result.get('error') if result.get('status') != 'success' else None
            )
            
            return result
            
        except Exception as e:
            # Handle exceptions
            self._collector.end_task(
                task_id=task_id,
                success=False,
                error_message=str(e)
            )
            raise
    
    def generate_sohh_report(self, output_dir: str = "reports") -> Optional[Path]:
        """
        Generate SOHH performance report.
        
        Args:
            output_dir: Directory to save the report
            
        Returns:
            Path to generated report, or None if failed
        """
        try:
            # Submit data to SOHH database
            self._collector.submit_to_sohh(db_path=self._db_path)
            
            # Generate visualization report
            from user_scoring.visualization_report import VisualizationReportGenerator
            
            generator = VisualizationReportGenerator(db_path=self._db_path)
            report_path = generator.generate_comprehensive_report(output_format="html")
            
            if report_path:
                print(f"\n📊 SOHH Report generated: {report_path}")
                return Path(report_path)
            else:
                print("⚠️  Failed to generate report")
                return None
                
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_sohh_stats(self) -> Dict[str, Any]:
        """
        Get current SOHH statistics.
        
        Returns:
            Dictionary with performance statistics
        """
        if not self._collector.task_executions:
            return {
                'total_tasks': 0,
                'successful_tasks': 0,
                'failed_tasks': 0,
                'success_rate': 0.0
            }
        
        total = len(self._collector.task_executions)
        successful = sum(1 for t in self._collector.task_executions if t.success)
        
        return {
            'total_tasks': total,
            'successful_tasks': successful,
            'failed_tasks': total - successful,
            'success_rate': (successful / total * 100) if total > 0 else 0.0
        }
    
    def __getattr__(self, name):
        """Delegate any other attributes to the underlying OpenSpace agent."""
        return getattr(self._agent, name)


# Convenience function for quick setup
def create_monitored_agent(config, project_id: str = "default", 
                          db_path: str = "data/openspace_sohh.db") -> MonitoredOpenSpace:
    """
    Create a monitored OpenSpace agent with minimal configuration.
    
    Args:
        config: OpenSpaceConfig instance
        project_id: Project identifier
        db_path: Database path
        
    Returns:
        MonitoredOpenSpace instance
    """
    return MonitoredOpenSpace(
        config=config,
        project_id=project_id,
        db_path=db_path
    )
