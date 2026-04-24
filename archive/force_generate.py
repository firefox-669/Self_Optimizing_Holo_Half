"""
强制生成新报告 - 带详细日志
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# 确保输出立即刷新
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

print("="*70, flush=True)
print("🚀 开始生成报告", flush=True)
print("="*70, flush=True)

try:
    # 导入模块
    print("\n[1/4] 导入模块...", flush=True)
    from user_scoring.visualization_report import VisualizationReportGenerator
    print("✓ 模块导入成功", flush=True)
    
    # 创建生成器
    print("\n[2/4] 创建报告生成器...", flush=True)
    generator = VisualizationReportGenerator(db_path="data/holo_half.db")
    print(f"✓ 生成器创建成功", flush=True)
    print(f"  数据库: {generator.db_path}", flush=True)
    print(f"  报告目录: {generator.report_dir}", flush=True)
    
    # 生成 HTML 报告
    print("\n[3/4] 生成 HTML 报告...", flush=True)
    html_report = generator.generate_comprehensive_report(output_format="html")
    
    if html_report:
        print(f"✓ HTML 报告生成成功!", flush=True)
        print(f"  文件路径: {html_report}", flush=True)
        print(f"  文件存在: {Path(html_report).exists()}", flush=True)
        if Path(html_report).exists():
            size = Path(html_report).stat().st_size
            print(f"  文件大小: {size} bytes ({size/1024:.1f} KB)", flush=True)
    else:
        print("✗ HTML 报告生成失败 (返回 None)", flush=True)
    
    # 生成 Markdown 报告
    print("\n[4/4] 生成 Markdown 报告...", flush=True)
    md_report = generator.generate_comprehensive_report(output_format="markdown")
    
    if md_report:
        print(f"✓ Markdown 报告生成成功!", flush=True)
        print(f"  文件路径: {md_report}", flush=True)
    else:
        print("✗ Markdown 报告生成失败 (返回 None)", flush=True)
    
    # 列出所有报告
    print("\n" + "="*70, flush=True)
    print("📊 当前 reports 目录中的所有报告:", flush=True)
    print("="*70, flush=True)
    
    reports_dir = Path("reports")
    if reports_dir.exists():
        files = sorted(reports_dir.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True)
        print(f"\n共找到 {len(files)} 个 HTML 报告:\n", flush=True)
        for i, f in enumerate(files[:5], 1):
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            size_kb = f.stat().st_size / 1024
            print(f"  {i}. {f.name}", flush=True)
            print(f"     大小: {size_kb:.1f} KB | 修改时间: {mtime}", flush=True)
    else:
        print("✗ reports 目录不存在", flush=True)
    
    print("\n" + "="*70, flush=True)
    print("✅ 报告生成完成！", flush=True)
    print("="*70, flush=True)
    
except Exception as e:
    print(f"\n❌ 发生错误: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
