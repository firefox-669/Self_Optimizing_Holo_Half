"""
OpenTelemetry Exporter 插件

将 SOHH 评估数据导出为 OpenTelemetry 格式，支持接入：
- Jaeger (分布式追踪)
- Prometheus (指标监控)
- Grafana (可视化)
- Zipkin (追踪系统)

设计理念：
- 标准化：使用 OpenTelemetry 标准协议
- 灵活性：支持多种后端存储
- 零侵入：不影响 SOHH 核心功能
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class OpenTelemetryExporter:
    """
    OpenTelemetry 数据导出器
    
    将 SOHH 的能力快照、任务执行记录等转换为 OpenTelemetry 格式
    """
    
    def __init__(self, service_name: str = "sohh-agent-evaluator"):
        """
        初始化导出器
        
        Args:
            service_name: 服务名称，用于标识数据来源
        """
        self.service_name = service_name
        self.exported_records = []
    
    def export_capability_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        将能力快照转换为 OpenTelemetry Metric 格式
        
        Args:
            snapshot: CapabilitySnapshot.to_dict() 的结果
            
        Returns:
            OpenTelemetry Metric 数据结构
        """
        timestamp_ns = int(datetime.fromisoformat(snapshot['timestamp']).timestamp() * 1e9)
        
        # 构建指标列表（七维能力）
        metrics = [
            {
                "name": "sohh.success_rate",
                "description": "Agent 任务成功率",
                "unit": "percent",
                "value": snapshot.get('success_rate', 0),
                "type": "gauge"
            },
            {
                "name": "sohh.efficiency_gain",
                "description": "效率提升百分比",
                "unit": "percent",
                "value": snapshot.get('efficiency_gain', 0),
                "type": "gauge"
            },
            {
                "name": "sohh.user_satisfaction",
                "description": "用户满意度评分",
                "unit": "percent",
                "value": snapshot.get('user_satisfaction', 0),
                "type": "gauge"
            },
            {
                "name": "sohh.usage_activity",
                "description": "使用活跃度",
                "unit": "percent",
                "value": snapshot.get('usage_activity', 0),
                "type": "gauge"
            },
            {
                "name": "sohh.cost_efficiency",
                "description": "成本效率评分",
                "unit": "percent",
                "value": snapshot.get('cost_efficiency', 0),
                "type": "gauge"
            },
            {
                "name": "sohh.innovation",
                "description": "创新性评分",
                "unit": "percent",
                "value": snapshot.get('innovation', 0),
                "type": "gauge"
            },
            {
                "name": "sohh.safety_score",
                "description": "安全性评分 (v2.1)",
                "unit": "percent",
                "value": snapshot.get('safety_score', 100),
                "type": "gauge"
            },
            {
                "name": "sohh.overall_score",
                "description": "综合评分（七维加权平均）",
                "unit": "percent",
                "value": snapshot.get('overall_score', 0),
                "type": "gauge"
            }
        ]
        
        # 构建 OpenTelemetry Metric 数据结构
        otel_metric = {
            "resourceMetrics": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": self.service_name}},
                            {"key": "agent.id", "value": {"stringValue": snapshot.get('agent_id', '')}},
                            {"key": "snapshot.id", "value": {"stringValue": snapshot.get('snapshot_id', '')}}
                        ]
                    },
                    "scopeMetrics": [
                        {
                            "scope": {
                                "name": "sohh.capability.evaluator",
                                "version": "2.1.0"
                            },
                            "metrics": [
                                {
                                    "name": metric["name"],
                                    "description": metric["description"],
                                    "unit": metric["unit"],
                                    "gauge": {
                                        "dataPoints": [
                                            {
                                                "timeUnixNano": str(timestamp_ns),
                                                "asDouble": metric["value"],
                                                "attributes": [
                                                    {"key": "dimension", "value": {"stringValue": metric["name"].split('.')[-1]}}
                                                ]
                                            }
                                        ]
                                    }
                                }
                                for metric in metrics
                            ]
                        }
                    ]
                }
            ]
        }
        
        self.exported_records.append({
            "type": "metric",
            "timestamp": snapshot['timestamp'],
            "data": otel_metric
        })
        
        return otel_metric
    
    def export_task_execution(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        将任务执行记录转换为 OpenTelemetry Span 格式
        
        Args:
            task: TaskExecution.to_dict() 的结果
            
        Returns:
            OpenTelemetry Span 数据结构
        """
        start_time_ns = int(datetime.fromisoformat(task['start_time']).timestamp() * 1e9) if task.get('start_time') else 0
        end_time_ns = int(datetime.fromisoformat(task['end_time']).timestamp() * 1e9) if task.get('end_time') else 0
        
        # 构建 Span 属性
        attributes = [
            {"key": "task.id", "value": {"stringValue": task.get('task_id', '')}},
            {"key": "agent.id", "value": {"stringValue": task.get('agent_id', '')}},
            {"key": "project.id", "value": {"stringValue": task.get('project_id', '')}},
            {"key": "task.status", "value": {"stringValue": task.get('status', '')}},
            {"key": "task.success", "value": {"boolValue": task.get('success', False)}},
            {"key": "task.duration_seconds", "value": {"doubleValue": task.get('duration_seconds', 0)}},
            {"key": "task.tokens_used", "value": {"intValue": str(task.get('tokens_used', 0))}},
            {"key": "task.cost", "value": {"doubleValue": task.get('cost', 0)}},
            {"key": "task.iterations", "value": {"intValue": str(task.get('iterations', 0))}}
        ]
        
        # 添加可选属性
        if task.get('code_quality_score'):
            attributes.append({
                "key": "task.code_quality",
                "value": {"doubleValue": task['code_quality_score']}
            })
        
        if task.get('test_pass_rate'):
            attributes.append({
                "key": "task.test_pass_rate",
                "value": {"doubleValue": task['test_pass_rate']}
            })
        
        if task.get('error_message'):
            attributes.append({
                "key": "task.error",
                "value": {"stringValue": task['error_message']}
            })
        
        # 构建 OpenTelemetry Span
        otel_span = {
            "resourceSpans": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": self.service_name}},
                            {"key": "agent.id", "value": {"stringValue": task.get('agent_id', '')}}
                        ]
                    },
                    "scopeSpans": [
                        {
                            "scope": {
                                "name": "sohh.task.executor",
                                "version": "2.1.0"
                            },
                            "spans": [
                                {
                                    "traceId": self._generate_trace_id(task.get('task_id', '')),
                                    "spanId": self._generate_span_id(task.get('task_id', '')),
                                    "parentSpanId": "",
                                    "name": f"agent.task.{task.get('status', 'unknown')}",
                                    "kind": 2,  # SPAN_KIND_SERVER
                                    "startTimeUnixNano": str(start_time_ns),
                                    "endTimeUnixNano": str(end_time_ns),
                                    "attributes": attributes,
                                    "status": {
                                        "code": 0 if task.get('success') else 2,  # OK or ERROR
                                        "message": task.get('error_message', '')
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        self.exported_records.append({
            "type": "span",
            "timestamp": task.get('start_time', ''),
            "data": otel_span
        })
        
        return otel_span
    
    def export_to_json_file(self, filepath: str) -> str:
        """
        将所有导出的记录保存到 JSON 文件
        
        Args:
            filepath: 输出文件路径
            
        Returns:
            文件路径
        """
        output = {
            "service": self.service_name,
            "export_time": datetime.now().isoformat(),
            "total_records": len(self.exported_records),
            "records": self.exported_records
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ OpenTelemetry 数据已导出到: {filepath}")
        return filepath
    
    def export_to_console(self, limit: int = 5) -> None:
        """
        将导出的记录打印到控制台（用于调试）
        
        Args:
            limit: 最多显示的记录数
        """
        print("="*70)
        print("📊 OpenTelemetry 导出数据预览")
        print("="*70)
        
        for i, record in enumerate(self.exported_records[:limit]):
            print(f"\n[{i+1}] 类型: {record['type']}")
            print(f"    时间: {record['timestamp']}")
            print(f"    数据: {json.dumps(record['data'], indent=2, ensure_ascii=False)[:500]}...")
        
        print(f"\n总计: {len(self.exported_records)} 条记录")
        print("="*70)
    
    def _generate_trace_id(self, task_id: str) -> str:
        """生成 Trace ID（基于 task_id 的哈希）"""
        import hashlib
        return hashlib.md5(task_id.encode()).hexdigest()[:32]
    
    def _generate_span_id(self, task_id: str) -> str:
        """生成 Span ID（基于 task_id 的哈希）"""
        import hashlib
        return hashlib.md5((task_id + "_span").encode()).hexdigest()[:16]


# ============================================================================
# 便捷函数
# ============================================================================

def create_exporter(service_name: str = "sohh-agent-evaluator") -> OpenTelemetryExporter:
    """
    创建 OpenTelemetry 导出器的便捷函数
    
    Args:
        service_name: 服务名称
        
    Returns:
        OpenTelemetryExporter 实例
    """
    return OpenTelemetryExporter(service_name=service_name)


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("🔌 SOHH OpenTelemetry Exporter 演示")
    print("="*70)
    
    # 创建导出器
    exporter = create_exporter("sohh-demo-agent")
    
    # 示例1：导出能力快照
    print("\n📋 示例1: 导出能力快照为 Metrics")
    print("-"*70)
    
    mock_snapshot = {
        "snapshot_id": "snap_001",
        "agent_id": "demo-agent-v1",
        "timestamp": datetime.now().isoformat(),
        "success_rate": 85.5,
        "efficiency_gain": 72.3,
        "user_satisfaction": 90.0,
        "usage_activity": 65.0,
        "cost_efficiency": 78.5,
        "innovation": 82.0,
        "safety_score": 95.0,  # v2.1 新增
        "overall_score": 81.2
    }
    
    metric_data = exporter.export_capability_snapshot(mock_snapshot)
    print(f"✅ 已转换 {len(metric_data['resourceMetrics'][0]['scopeMetrics'][0]['metrics'])} 个指标")
    
    # 示例2：导出任务执行记录
    print("\n📋 示例2: 导出任务执行为 Spans")
    print("-"*70)
    
    mock_task = {
        "task_id": "task_001",
        "agent_id": "demo-agent-v1",
        "project_id": "demo-project",
        "description": "Create a Flask API endpoint",
        "status": "success",
        "start_time": datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "duration_seconds": 125.5,
        "success": True,
        "tokens_used": 2500,
        "cost": 0.0125,
        "iterations": 8,
        "code_quality_score": 0.88,
        "test_pass_rate": 0.95
    }
    
    span_data = exporter.export_task_execution(mock_task)
    print(f"✅ 已转换 Span: {span_data['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['name']}")
    
    # 示例3：导出到文件
    print("\n📋 示例3: 导出到 JSON 文件")
    print("-"*70)
    
    filepath = "data/otel_export_demo.json"
    exporter.export_to_json_file(filepath)
    
    # 示例4：打印到控制台
    print("\n📋 示例4: 控制台预览")
    print("-"*70)
    
    exporter.export_to_console(limit=2)
    
    print("\n" + "="*70)
    print("💡 提示: 导出的数据可以发送到:")
    print("   - Jaeger: http://localhost:14268/api/traces")
    print("   - Prometheus: 通过 OTLP Receiver")
    print("   - Grafana: 通过 Tempo 或 Loki")
    print("="*70)
