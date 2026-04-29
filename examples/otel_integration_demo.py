"""
OpenTelemetry 集成示例

演示如何将 SOHH 评估数据导出为 OpenTelemetry 格式，
并发送到主流可观测性平台（Jaeger、Prometheus、Grafana）
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sohh_standard_interface import SOHHDataCollector
from plugins import OpenTelemetryExporter, calculate_security_score


def demo_otel_integration():
    """演示完整的 OpenTelemetry 集成流程"""
    
    print("="*70)
    print("🔌 SOHH + OpenTelemetry 集成演示")
    print("="*70)
    
    # 步骤1: 创建 SOHH 数据采集器
    print("\n📋 步骤1: 创建 SOHH 数据采集器")
    print("-"*70)
    
    collector = SOHHDataCollector(
        agent_id="otel-demo-agent",
        project_id="otel-integration-test"
    )
    
    print(f"✅ 采集器已创建: {collector.agent_id}")
    
    # 步骤2: 记录任务执行
    print("\n📋 步骤2: 记录任务执行")
    print("-"*70)
    
    task_id = "otel-task-001"
    collector.start_task(
        task_id=task_id,
        description="Build a REST API with authentication",
        metadata={"framework": "AutoGen"}
    )
    
    # 模拟一些执行步骤
    mock_steps = [
        {"content": "pip install flask"},
        {"content": "python app.py"},
        {"content": "curl http://localhost:5000/api/test"}
    ]
    
    # 计算安全评分
    safety_score = calculate_security_score(mock_steps)
    print(f"✅ 安全评分: {safety_score}/100")
    
    # 结束任务
    collector.end_task(
        task_id=task_id,
        success=True,
        tokens_used=3500,
        cost=0.0175,
        iterations=12,
        code_quality_score=0.90,
        test_pass_rate=0.98,
        metadata={
            "safety_score": safety_score
        }
    )
    
    print(f"✅ 任务记录完成: {task_id}")
    
    # 步骤3: 拍摄能力快照
    print("\n📋 步骤3: 拍摄能力快照")
    print("-"*70)
    
    snapshot = collector.take_capability_snapshot()
    
    print(f"✅ 能力快照已生成:")
    print(f"   成功率: {snapshot.success_rate:.2f}")
    print(f"   效率: {snapshot.efficiency_gain:.2f}")
    print(f"   满意度: {snapshot.user_satisfaction:.2f}")
    print(f"   活跃度: {snapshot.usage_activity:.2f}")
    print(f"   成本效率: {snapshot.cost_efficiency:.2f}")
    print(f"   创新性: {snapshot.innovation:.2f}")
    print(f"   安全性: {snapshot.safety_score:.2f} (v2.1)")
    print(f"   综合评分: {snapshot.overall_score:.2f}")
    
    # 步骤4: 提交到 SOHH 数据库
    print("\n📋 步骤4: 提交到 SOHH 数据库")
    print("-"*70)
    
    result = collector.submit_to_sohh(db_path="data/holo_half.db")
    print(f"✅ 数据已提交: {result}")
    
    # 步骤5: 创建 OpenTelemetry 导出器
    print("\n📋 步骤5: 创建 OpenTelemetry 导出器")
    print("-"*70)
    
    exporter = OpenTelemetryExporter(service_name="sohh-production-agent")
    print(f"✅ 导出器已创建: {exporter.service_name}")
    
    # 步骤6: 导出能力快照为 Metrics
    print("\n📋 步骤6: 导出能力快照为 OpenTelemetry Metrics")
    print("-"*70)
    
    snapshot_dict = snapshot.to_dict()
    metric_data = exporter.export_capability_snapshot(snapshot_dict)
    
    metrics_count = len(metric_data['resourceMetrics'][0]['scopeMetrics'][0]['metrics'])
    print(f"✅ 已转换 {metrics_count} 个指标:")
    
    for metric in metric_data['resourceMetrics'][0]['scopeMetrics'][0]['metrics']:
        value = metric['gauge']['dataPoints'][0]['asDouble']
        name = metric['name'].split('.')[-1]
        print(f"   • {name}: {value:.2f}")
    
    # 步骤7: 导出任务执行为 Spans
    print("\n📋 步骤7: 导出任务执行为 OpenTelemetry Spans")
    print("-"*70)
    
    task_dict = collector.task_executions[0].to_dict()
    span_data = exporter.export_task_execution(task_dict)
    
    span = span_data['resourceSpans'][0]['scopeSpans'][0]['spans'][0]
    print(f"✅ 已转换 Span:")
    print(f"   名称: {span['name']}")
    print(f"   Trace ID: {span['traceId'][:16]}...")
    print(f"   状态: {'SUCCESS' if span['status']['code'] == 0 else 'ERROR'}")
    
    # 步骤8: 导出到文件
    print("\n📋 步骤8: 导出到 JSON 文件")
    print("-"*70)
    
    filepath = "data/sohh_otel_export.json"
    exporter.export_to_json_file(filepath)
    
    # 步骤9: 显示如何发送到后端
    print("\n📋 步骤9: 发送到可观测性后端")
    print("-"*70)
    
    print("\n💡 可以将导出的数据发送到以下平台:\n")
    
    print("1️⃣  Jaeger (分布式追踪)")
    print("   命令: curl -X POST http://localhost:14268/api/traces \\")
    print("         -H 'Content-Type: application/json' \\")
    print(f"         -d @{filepath}\n")
    
    print("2️⃣  Prometheus (指标监控)")
    print("   配置 otel-collector-config.yaml:")
    print("   receivers:")
    print("     otlp:")
    print("       protocols:")
    print("         http:")
    print("   exporters:")
    print("     prometheus:")
    print("       endpoint: '0.0.0.0:8889'\n")
    
    print("3️⃣  Grafana Tempo (追踪可视化)")
    print("   配置 tempo.yaml:")
    print("   server:")
    print("     http_listen_port: 3200")
    print("   distributor:")
    print("     receivers:")
    print("       otlp:")
    print("         protocols:")
    print("           http:\n")
    
    print("4️⃣  Honeycomb (SaaS 可观测性)")
    print("   命令: curl -X POST https://api.honeycomb.io/1/events/sohh \\")
    print("         -H 'X-Honeycomb-Team: YOUR_API_KEY' \\")
    print(f"         -d @{filepath}\n")
    
    print("="*70)
    print("✅ OpenTelemetry 集成演示完成！")
    print("="*70)
    
    return exporter


if __name__ == "__main__":
    exporter = demo_otel_integration()
    
    print("\n🎯 下一步:")
    print("   1. 安装 OpenTelemetry Collector: https://opentelemetry.io/docs/collector/")
    print("   2. 配置接收器接收 SOHH 数据")
    print("   3. 在 Grafana/Jaeger 中查看可视化面板")
    print("   4. 设置告警规则监控 Agent 性能")
