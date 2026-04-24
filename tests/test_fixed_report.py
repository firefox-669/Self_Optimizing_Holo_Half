"""测试修复后的报告生成"""
import sys
import traceback

try:
    print("开始导入模块...")
    from user_scoring import VisualizationReportGenerator
    
    print("创建生成器...")
    generator = VisualizationReportGenerator(db_path="data/holo_half.db")
    
    print("生成 HTML 报告...")
    html_report = generator.generate_comprehensive_report(output_format="html")
    
    if html_report:
        print(f"✅ HTML 报告成功生成!")
        print(f"   文件: {html_report}")
    else:
        print("❌ HTML 报告生成失败")
    
    print("\n生成 Markdown 报告...")
    md_report = generator.generate_comprehensive_report(output_format="markdown")
    
    if md_report:
        print(f"✅ Markdown 报告成功生成!")
        print(f"   文件: {md_report}")
    else:
        print("❌ Markdown 报告生成失败")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    traceback.print_exc()
    sys.exit(1)
