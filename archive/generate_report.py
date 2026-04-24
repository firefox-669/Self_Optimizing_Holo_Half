"""
快速生成可视化报告

根据 my_direction 战略要求，一键生成精美的评估报告
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from user_scoring import VisualizationReportGenerator


def main():
    """主函数"""
    print("="*70)
    print("🚀 SOHH 可视化报告生成器")
    print("="*70)
    print()
    
    # 创建报告生成器
    generator = VisualizationReportGenerator()
    
    # 生成 HTML 报告（推荐）
    print("📊 正在生成 HTML 报告...")
    html_report = generator.generate_comprehensive_report(output_format="html")
    
    if html_report:
        print(f"✅ HTML 报告已生成: {html_report}")
        print(f"💡 提示: 在浏览器中打开查看精美的可视化效果")
    
    print()
    
    # 生成 Markdown 报告（备选）
    print("📝 正在生成 Markdown 报告...")
    md_report = generator.generate_comprehensive_report(output_format="markdown")
    
    if md_report:
        print(f"✅ Markdown 报告已生成: {md_report}")
    
    print()
    print("="*70)
    print("🎉 报告生成完成！")
    print("="*70)
    print()
    print("📄 报告位置:")
    if html_report:
        print(f"   HTML:  {html_report}")
    if md_report:
        print(f"   Markdown: {md_report}")
    print()
    print("💡 下一步:")
    print("   1. 打开 HTML 报告查看精美的可视化图表")
    print("   2. 将报告分享到 GitHub/社交媒体")
    print("   3. 用数据证明 AI Agent 的自进化能力")
    print()


if __name__ == "__main__":
    main()
