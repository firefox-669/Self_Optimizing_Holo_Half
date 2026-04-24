"""快速测试报告生成"""
import sqlite3
from pathlib import Path

db_path = Path("data/holo_half.db")

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("="*60)
    print("📊 数据库状态")
    print("="*60)
    print(f"数据库文件: {db_path}")
    print(f"表列表: {tables}")
    print()
    
    # 检查每个表的记录数
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} 条记录")
    
    conn.close()
    print()
else:
    print("❌ 数据库文件不存在")

print("="*60)
print("🚀 开始生成报告...")
print("="*60)
print()

try:
    from user_scoring import VisualizationReportGenerator
    
    generator = VisualizationReportGenerator(db_path="data/holo_half.db")
    
    print("📊 生成 HTML 报告...")
    html_report = generator.generate_comprehensive_report(output_format="html")
    
    if html_report:
        print(f"✅ HTML 报告成功生成!")
        print(f"   文件位置: {html_report}")
        print(f"   💡 在浏览器中打开查看精美图表")
    else:
        print("⚠️  HTML 报告生成失败（可能没有数据）")
    
    print()
    print("📝 生成 Markdown 报告...")
    md_report = generator.generate_comprehensive_report(output_format="markdown")
    
    if md_report:
        print(f"✅ Markdown 报告成功生成!")
        print(f"   文件位置: {md_report}")
    
    print()
    print("="*60)
    print("🎉 测试完成！")
    print("="*60)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
