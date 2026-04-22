"""
深度分析引擎
生成项目的深度分析报告
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
import hashlib


class DeepAnalyzer:
    """
    深度分析引擎
    生成项目的深度分析报告
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.analysis_dir = self.workspace / ".sohh_cache" / "deep_analysis"
        self.analysis_dir.mkdir(exist_ok=True)
    
    async def analyze(
        self,
        existing_analysis: Dict[str, Any] = None,
        project_analysis: Dict[str, Any] = None,
        info_analysis: List[Dict] = None,
    ) -> Dict[str, Any]:
        """生成深度分析报告"""
        
        # 能力评分
        capability_scores = self._calculate_capability_scores(
            existing_analysis,
            project_analysis
        )
        
        # 弱点识别
        weaknesses = self._identify_weaknesses(
            existing_analysis,
            project_analysis
        )
        
        # 优化机会
        opportunities = self._find_optimization_opportunities(
            info_analysis,
            project_analysis
        )
        
        # 比对基线
        comparison = await self._compare_with_baseline(capability_scores)
        
        # 建议
        recommendations = self._generate_recommendations(
            weaknesses,
            opportunities,
            capability_scores
        )
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "capability_scores": capability_scores,
            "weaknesses": weaknesses,
            "optimization_opportunities": opportunities,
            "comparison_with_baseline": comparison,
            "recommendations": recommendations,
        }
        
        # 保存分析
        self._save_analysis(analysis)
        
        return analysis
    
    def _calculate_capability_scores(
        self,
        existing: Dict[str, Any],
        project: Dict[str, Any],
    ) -> Dict[str, float]:
        """计算能力评分"""
        scores = {
            "execution": 0.5,
            "evolution": 0.5,
            "safety": 0.5,
            "integration": 0.5,
            "self_analysis": 0.5,
            "overall": 0.5,
        }
        
        # 从项目分析获取
        if project:
            project_scores = project.get("capabilities", {})
            for key in ["execution", "evolution", "safety", "integration"]:
                if key in project_scores:
                    scores[key] = project_scores[key]
        
        # 计算总分
        total = sum(scores.values()) - scores["overall"]
        scores["overall"] = round(total / (len(scores) - 1), 3)
        
        return scores
    
    def _identify_weaknesses(
        self,
        existing: Dict[str, Any],
        project: Dict[str, Any],
    ) -> List[Dict]:
        """识别弱点"""
        weaknesses = []
        
        # 从项目分析识别
        if project:
            capabilities = project.get("capabilities", {})
            
            for capability, score in capabilities.items():
                if capability == "overall":
                    continue
                
                if score < 0.6:
                    weaknesses.append({
                        "component": capability,
                        "issue": f"{capability} 能力评分过低: {score:.2f}",
                        "severity": "high" if score < 0.4 else "medium",
                        "score": score,
                    })
        
        # 从现有分析识别
        if existing:
            # OpenHands 连接问题
            if not existing.get("openhands", {}).get("connected"):
                weaknesses.append({
                    "component": "openhands",
                    "issue": "OpenHands 未连接",
                    "severity": "high",
                })
            
            # OpenSpace 连接问题
            if not existing.get("openspace", {}).get("connected"):
                weaknesses.append({
                    "component": "openspace",
                    "issue": "OpenSpace 未连接",
                    "severity": "high",
                })
        
        # 排序
        severity_order = {"high": 0, "medium": 1, "low": 2}
        weaknesses.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 2))
        
        return weaknesses
    
    def _find_optimization_opportunities(
        self,
        info: List[Dict],
        project: Dict[str, Any],
    ) -> List[Dict]:
        """发现优化机会"""
        opportunities = []
        
        # 从资讯分析发现
        if info:
            for item in info[:10]:
                opportunities.append({
                    "type": item.get("type", "enhancement"),
                    "description": item.get("improvement", "")[:100],
                    "source": item.get("source_info", {}).get("source", "unknown"),
                    "priority": item.get("priority", 0.5),
                })
        
        # 从项目分析发现
        if project:
            health = project.get("health_metrics", {})
            
            if not health.get("has_tests"):
                opportunities.append({
                    "type": "test_coverage",
                    "description": "添加测试覆盖",
                    "source": "project_analysis",
                    "priority": 0.5,
                })
        
        # 排序
        opportunities.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        return opportunities
    
    async def _compare_with_baseline(
        self,
        current_scores: Dict[str, float],
    ) -> Dict[str, Any]:
        """与基线比较"""
        
        # 加载基线
        baseline_file = self.workspace / ".sohh_cache" / "capability_baseline.json"
        baseline_scores = {}
        
        if baseline_file.exists():
            with open(baseline_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                baseline_scores = data.get("baseline", {})
        
        if not baseline_scores:
            # 首次分析，保存基线
            baseline_scores = current_scores.copy()
            self._save_baseline(baseline_scores)
            
            return {
                "improved": False,
                "is_baseline": True,
                "baseline": baseline_scores,
                "current": current_scores,
                "delta": 0,
            }
        
        # 计算变化
        overall_current = current_scores.get("overall", 0)
        overall_baseline = baseline_scores.get("overall", 0)
        delta = overall_current - overall_baseline
        
        return {
            "improved": delta > 0,
            "is_baseline": False,
            "baseline": baseline_scores,
            "current": current_scores,
            "delta": round(delta, 3),
            "details": {
                key: round(current_scores.get(key, 0) - baseline_scores.get(key, 0), 
                for key in current_scores
            },
        }
    
    def _save_baseline(self, scores: Dict[str, float]):
        """保存基线"""
        baseline_file = self.workspace / ".sohh_cache" / "capability_baseline.json"
        baseline_file.parent.mkdir(exist_ok=True)
        
        with open(baseline_file, "w", encoding="utf-8") as f:
            json.dump({
                "baseline": scores,
                "updated": datetime.now().isoformat(),
            }, f, indent=2)
    
    def _generate_recommendations(
        self,
        weaknesses: List[Dict],
        opportunities: List[Dict],
        scores: Dict[str, float],
    ) -> List[Dict]:
        """生成建议"""
        recommendations = []
        
        # 基于弱点
        for weakness in weaknesses[:5]:
            recommendations.append({
                "priority": 10 - weakness.get("severity", "medium") == "high" and 8 or 5,
                "action": f"修复 {weakness.get('component')}: {weakness.get('issue')}",
                "reason": weakness.get("issue", ""),
                "type": "fix",
            })
        
        # 基于机会
        for opp in opportunities[:5]:
            recommendations.append({
                "priority": int(opp.get("priority", 0.5) * 10),
                "action": f"把握优化机会: {opp.get('description', '')}",
                "reason": opp.get("description", ""),
                "type": "opportunity",
            })
        
        # 排序
        recommendations.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        return recommendations
    
    def _save_analysis(self, analysis: Dict):
        """保存分析"""
        # 按日期保存
        date = datetime.now().strftime("%Y-%m-%d")
        analysis_file = self.analysis_dir / f"analysis_{date}.json"
        
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, default=str)
    
    def get_latest_analysis(self) -> Dict:
        """获取最新分析"""
        analysis_files = sorted(self.analysis_dir.glob("analysis_*.json"))
        
        if not analysis_files:
            return {}
        
        with open(analysis_files[-1], "r", encoding="utf-8") as f:
            return json.load(f)
    
    def generate_markdown(self, analysis: Dict) -> str:
        """生成 Markdown 格式报告"""
        
        scores = analysis.get("capability_scores", {})
        weaknesses = analysis.get("weaknesses", [])
        opportunities = analysis.get("optimization_opportunities", [])
        recommendations = analysis.get("recommendations", [])
        comparison = analysis.get("comparison_with_baseline", {})
        
        md = f"""# 深度分析报告

生成时间: {analysis.get('timestamp', '')}

## 能力评分

| 能力 | 评分 |
|------|------|
| 执行能力 | {scores.get('execution', 0):.2f} |
| 进化能力 | {scores.get('evolution', 0):.2f} |
| 安全能力 | {scores.get('safety', 0):.2f} |
| 集成能力 | {scores.get('integration', 0):.2f} |
| 自分析能力 | {scores.get('self_analysis', 0):.2f} |
| **总分** | **{scores.get('overall', 0):.2f}** |

## 弱点

"""
        
        if not weaknesses:
            md += "*未发现明显弱点*\n"
        else:
            for w in weaknesses:
                md += f"- [{w.get('severity', '?').upper()}] {w.get('component')}: {w.get('issue')}\n"
        
        md += """
## 优化机会

"""
        
        if not opportunities:
            md += "*无优化机会*\n"
        else:
            for o in opportunities[:5]:
                md += f"- [{o.get('priority', 0):.1f}] {o.get('description')}\n"
        
        md += f"""
## 基线对比

- 改进: {'是' if comparison.get('improved') else '否'}
- 变化: {comparison.get('delta', 0):+.3f}

## 建议

"""
        
        for r in recommendations[:5]:
            md += f"- [{r.get('priority', 0)}] {r.get('action')}\n"
        
        return md