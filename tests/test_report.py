"""
简单测试：生成报告
"""

import sys
from pathlib import Path

# 添加项目根目录
sys.path.insert(0, str(Path(__file__).parent))

print("🚀 开始生成报告...")

try:
    from user_scoring import VisualizationReportGenerator
    
    generator = VisualizationReportGenerator(db_path="data/holo_half.db")
    
    print("📊 生成 HTML 报告...")
    html_report = generator.generate_comprehensive_report(output_format="html")
    
    if html_report:
        print(f"✅ HTML 报告成功生成: {html_report}")
    else:
        print("⚠️  报告生成失败（可能没有数据）")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
