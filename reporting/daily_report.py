"""
每日简报生成器
生成项目每日状态报告
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timedelta


class DailyReportGenerator:
    """
    每日简报生成器
    生成项目每日状态简报
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.reports_dir = self.workspace / ".sohh_cache" / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    async def generate(
        self,
        execution_stats: Dict[str, Any] = None,
        evolution_stats: Dict[str, Any] = None,
        suggestions: List[Dict] = None,
        health: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """生成每日简报"""
        
        date = datetime.now().strftime("%Y-%m-%d")
        
        summary = {
            "tasks_executed": execution_stats.get("total", 0) if execution_stats else 0,
            "success_rate": execution_stats.get("success_rate", 0) if execution_stats else 0,
            "skills_evolved": evolution_stats.get("total", 0) if evolution_stats else 0,
            "optimizations_applied": len([s for s in (suggestions or []) if s.get("status") == "applied"]),
            "project_health_score": health.get("overall", 0.5) if health else 0.5,
        }
        
        # 今日变更
        changes = self._get_today_changes()
        
        # 待处理建议
        pending = [
            {
                "id": s.get("id"),
                "title": s.get("title"),
                "priority": s.get("priority"),
            }
            for s in (suggestions or [])
            if s.get("status") == "pending"
        ][:5]
        
        report = {
            "date": date,
            "summary": summary,
            "changes": changes,
            "pending_suggestions": pending,
            "project_health": health or {},
            "generated_at": datetime.now().isoformat(),
        }
        
        # 保存报告
        self._save_report(date, report)
        
        return report
    
    def _get_today_changes(self) -> List[Dict]:
        """获取今日变更"""
        changes_file = self.workspace / ".sohh_cache" / "changes" / "all_changes.json"
        
        if not changes_file.exists():
            return []
        
        with open(changes_file, "r", encoding="utf-8") as f:
            all_changes = json.load(f)
        
        today = datetime.now().date()
        today_changes = []
        
        for change in all_changes:
            timestamp = change.get("timestamp", "")
            if not timestamp:
                continue
            
            try:
                dt = datetime.fromisoformat(timestamp)
                if dt.date() == today:
                    today_changes.append({
                        "type": change.get("type"),
                        "description": change.get("description"),
                        "timestamp": timestamp,
                    })
            except:
                pass
        
        return today_changes
    
    def _save_report(self, date: str, report: Dict):
        """保存报告"""
        report_file = self.reports_dir / f"daily_{date}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
    
    def get_report(self, date: str = None) -> Dict:
        """获取指定日期的报告"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        report_file = self.reports_dir / f"daily_{date}.json"
        
        if not report_file.exists():
            return {}
        
        with open(report_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_recent_reports(self, days: int = 7) -> List[Dict]:
        """获取最近的报告"""
        reports = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            report = self.get_report(date)
            if report:
                reports.append(report)
        
        return reports
    
    def generate_markdown(self, report: Dict) -> str:
        """生成 Markdown 格式报告"""
        date = report.get("date", "")
        summary = report.get("summary", {})
        
        md = f"""# 每日简报 - {date}

## 概览

| 指标 | 数值 |
|------|------|
| 执行任务数 | {summary.get('tasks_executed', 0)} |
| 成功率 | {summary.get('success_rate', 0):.1%} |
| Skills 进化 | {summary.get('skills_evolved', 0)} |
| 优化应用 | {summary.get('optimizations_applied', 0)} |
| 项目健康度 | {summary.get('project_health_score', 0):.2f} |

## 今日变更

"""
        
        changes = report.get("changes", [])
        if not changes:
            md += "*今日无变更*\n"
        else:
            for change in changes:
                md += f"- {change.get('type')}: {change.get('description')}\n"
        
        md += """
## 待处理建议

"""
        
        suggestions = report.get("pending_suggestions", [])
        if not suggestions:
            md += "*无待处理建议*\n"
        else:
            for s in suggestions:
                md += f"- [{s.get('priority', 0):.1f}] {s.get('title')}\n"
        
        return md