"""
SOHH 定时报告生成器

自动生成安全评估日报/周报/月报
支持邮件通知
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 添加插件路径
sys.path.insert(0, str(Path(__file__).parent / "plugins"))

from security_assessor import SecurityAssessor


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, db_path: str = None):
        self.assessor = SecurityAssessor(db_path)
        self.report_dir = Path(__file__).parent / "reports"
        self.report_dir.mkdir(exist_ok=True)
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """生成日报"""
        print("📊 生成日报...")
        
        # 获取今天的评估记录
        today = datetime.now().strftime("%Y-%m-%d")
        history = self.assessor.get_assessment_history(limit=1000)
        
        # 过滤今天的记录
        today_reports = [
            r for r in history
            if r['created_at'].startswith(today)
        ]
        
        # 统计分析
        stats = self._analyze_reports(today_reports)
        
        # 生成报告内容
        report = {
            'report_type': 'daily',
            'date': today,
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'recommendations': self._generate_recommendations(stats),
            'summary': self._generate_summary(stats)
        }
        
        # 保存报告
        report_file = self.report_dir / f"daily_report_{today}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成Markdown版本
        md_file = self.report_dir / f"daily_report_{today}.md"
        self._save_markdown_report(report, md_file)
        
        print(f"✅ 日报已保存: {report_file}")
        return report
    
    def generate_weekly_report(self) -> Dict[str, Any]:
        """生成周报"""
        print("📊 生成周报...")
        
        # 获取过去7天的记录
        history = self.assessor.get_assessment_history(limit=5000)
        
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        weekly_reports = [
            r for r in history
            if r['created_at'] >= seven_days_ago
        ]
        
        # 统计分析
        stats = self._analyze_reports(weekly_reports)
        
        # 生成报告
        report = {
            'report_type': 'weekly',
            'period': f"{seven_days_ago} to {datetime.now().strftime('%Y-%m-%d')}",
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'trends': self._analyze_trends(weekly_reports),
            'recommendations': self._generate_recommendations(stats),
            'summary': self._generate_summary(stats)
        }
        
        # 保存报告
        week_num = datetime.now().isocalendar()[1]
        report_file = self.report_dir / f"weekly_report_w{week_num}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 周报已保存: {report_file}")
        return report
    
    def _analyze_reports(self, reports: List[Dict]) -> Dict[str, Any]:
        """分析报告统计数据"""
        if not reports:
            return {
                'total_assessments': 0,
                'avg_safety_score': 0,
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'low_risk_count': 0
            }
        
        total = len(reports)
        avg_score = sum(r['score'] for r in reports) / total
        
        high_risk = sum(1 for r in reports if r['score'] < 50)
        medium_risk = sum(1 for r in reports if 50 <= r['score'] < 80)
        low_risk = sum(1 for r in reports if r['score'] >= 80)
        
        return {
            'total_assessments': total,
            'avg_safety_score': round(avg_score, 2),
            'high_risk_count': high_risk,
            'medium_risk_count': medium_risk,
            'low_risk_count': low_risk,
            'high_risk_percentage': round(high_risk / total * 100, 2),
            'medium_risk_percentage': round(medium_risk / total * 100, 2),
            'low_risk_percentage': round(low_risk / total * 100, 2)
        }
    
    def _analyze_trends(self, reports: List[Dict]) -> Dict[str, Any]:
        """分析趋势"""
        if len(reports) < 2:
            return {'trend': 'insufficient_data'}
        
        # 按日期分组
        daily_scores = {}
        for report in reports:
            date = report['created_at'][:10]
            if date not in daily_scores:
                daily_scores[date] = []
            daily_scores[date].append(report['score'])
        
        # 计算每日平均分
        daily_avgs = {
            date: sum(scores) / len(scores)
            for date, scores in daily_scores.items()
        }
        
        # 判断趋势
        dates = sorted(daily_avgs.keys())
        if len(dates) >= 2:
            first_half = [daily_avgs[d] for d in dates[:len(dates)//2]]
            second_half = [daily_avgs[d] for d in dates[len(dates)//2:]]
            
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            
            if avg_second > avg_first + 5:
                trend = 'improving'
            elif avg_second < avg_first - 5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'daily_averages': daily_avgs,
            'change': round(avg_second - avg_first, 2) if len(dates) >= 2 else 0
        }
    
    def _generate_recommendations(self, stats: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if stats['total_assessments'] == 0:
            return ["暂无数据，建议开始进行安全评估"]
        
        if stats['high_risk_percentage'] > 20:
            recommendations.append(
                f"⚠️ 高风险评估占比{stats['high_risk_percentage']}%，建议加强安全防护措施"
            )
        
        if stats['avg_safety_score'] < 70:
            recommendations.append(
                f"📉 平均安全评分{stats['avg_safety_score']}分，低于标准线，需要改进"
            )
        
        if stats['high_risk_count'] > 0:
            recommendations.append(
                f"🔴 发现{stats['high_risk_count']}个高风险项，需要立即处理"
            )
        
        recommendations.append("💡 建议定期进行红队测试，发现潜在漏洞")
        recommendations.append("📊 建议建立Skills信誉系统，防止恶意代码")
        
        return recommendations
    
    def _generate_summary(self, stats: Dict) -> str:
        """生成摘要"""
        if stats['total_assessments'] == 0:
            return "今日暂无安全评估记录"
        
        summary = (
            f"本期共完成{stats['total_assessments']}次安全评估，"
            f"平均安全评分{stats['avg_safety_score']}分。"
        )
        
        if stats['high_risk_count'] > 0:
            summary += f"发现{stats['high_risk_count']}个高风险项，"
        
        if stats['avg_safety_score'] >= 80:
            summary += "整体安全性良好。"
        elif stats['avg_safety_score'] >= 60:
            summary += "安全性一般，需要改进。"
        else:
            summary += "安全性较差，需要立即采取措施。"
        
        return summary
    
    def _save_markdown_report(self, report: Dict, file_path: Path):
        """保存Markdown格式报告"""
        stats = report['statistics']
        
        md_content = f"""# SOHH 安全评估{report['report_type'].capitalize()}报告

**生成时间**: {report['generated_at']}
**报告类型**: {report['report_type']}

## 📊 统计概览

- **总评估次数**: {stats['total_assessments']}
- **平均安全评分**: {stats['avg_safety_score']}/100
- **高风险项**: {stats['high_risk_count']} ({stats.get('high_risk_percentage', 0)}%)
- **中风险项**: {stats['medium_risk_count']} ({stats.get('medium_risk_percentage', 0)}%)
- **低风险项**: {stats['low_risk_count']} ({stats.get('low_risk_percentage', 0)}%)

## 📝 摘要

{report['summary']}

## 💡 改进建议

"""
        
        for i, rec in enumerate(report['recommendations'], 1):
            md_content += f"{i}. {rec}\n"
        
        if 'trends' in report:
            trends = report['trends']
            md_content += f"\n## 📈 趋势分析\n\n"
            md_content += f"- **整体趋势**: {trends.get('trend', 'N/A')}\n"
            if 'change' in trends:
                md_content += f"- **变化幅度**: {trends['change']:+.2f}分\n"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)


def main():
    """主函数"""
    generator = ReportGenerator()
    
    print("="*70)
    print("📊 SOHH 定时报告生成器")
    print("="*70)
    
    # 生成日报
    daily_report = generator.generate_daily_report()
    print(f"\n📄 日报摘要: {daily_report['summary']}")
    
    # 生成周报
    weekly_report = generator.generate_weekly_report()
    print(f"\n📄 周报摘要: {weekly_report['summary']}")
    
    print("\n" + "="*70)
    print("✅ 报告生成完成！")
    print("="*70)


if __name__ == "__main__":
    main()
