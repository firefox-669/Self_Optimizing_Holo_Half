"""
OpenSpace Skill 分析器

分析 Skills 的覆盖度、使用情况和进化潜力
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class SkillAnalyzer:
    """
    OpenSpace Skill 分析器
    
    分析内容:
    - Skill 覆盖度（哪些领域有/没有 Skill）
    - Skill 使用频率和效果
    - Skill 质量评分
    - 进化机会识别
    """
    
    def __init__(self, openspace_client=None):
        self.client = openspace_client
        self.analysis_cache: Dict[str, Any] = {}
    
    async def analyze(self) -> Dict[str, Any]:
        """
        全面分析 OpenSpace Skills
        
        Returns:
            {
                "total_skills": 50,
                "skill_coverage": {...},
                "usage_statistics": {...},
                "quality_metrics": {...},
                "evolution_opportunities": [...],
                "analyzed_at": "..."
            }
        """
        # 获取 Skills 列表
        skills = await self._get_skills()
        
        # 分析覆盖度
        coverage = self._analyze_coverage(skills)
        
        # 分析使用情况
        usage_stats = await self._analyze_usage(skills)
        
        # 评估质量
        quality = self._evaluate_quality(skills)
        
        # 识别进化机会
        opportunities = self._identify_opportunities(skills, coverage, quality)
        
        result = {
            "total_skills": len(skills),
            "active_skills": sum(1 for s in skills if s.get("is_active", True)),
            "skill_coverage": coverage,
            "usage_statistics": usage_stats,
            "quality_metrics": quality,
            "evolution_opportunities": opportunities,
            "recommendations": self._generate_recommendations(coverage, quality, opportunities),
            "analyzed_at": datetime.now().isoformat()
        }
        
        # 缓存结果
        self.analysis_cache = result
        
        return result
    
    async def _get_skills(self) -> List[Dict[str, Any]]:
        """获取 Skills 列表"""
        try:
            if self.client and hasattr(self.client, 'get_skills'):
                return await self.client.get_skills()
            
            # 如果没有客户端，返回空列表
            return []
        except Exception as e:
            print(f"⚠️ Failed to get skills: {e}")
            return []
    
    def _analyze_coverage(self, skills: List[Dict]) -> Dict[str, Any]:
        """
        分析 Skill 覆盖度
        
        按领域分类:
        - 编程开发
        - 数据分析
        - 文档处理
        - DevOps
        - 测试
        - 其他
        """
        categories = {
            "programming": 0,
            "data_analysis": 0,
            "documentation": 0,
            "devops": 0,
            "testing": 0,
            "other": 0
        }
        
        category_skills = {k: [] for k in categories.keys()}
        
        for skill in skills:
            category = self._categorize_skill(skill)
            categories[category] += 1
            category_skills[category].append(skill.get("name", "unknown"))
        
        total = len(skills)
        
        return {
            "by_category": categories,
            "category_details": {
                cat: {
                    "count": count,
                    "percentage": round(count / max(total, 1) * 100, 2),
                    "skills": skills_list[:5]  # 只显示前 5 个
                }
                for cat, count, skills_list in [
                    (k, v, category_skills[k]) for k, v in categories.items()
                ]
            },
            "coverage_score": self._calculate_coverage_score(categories),
            "gaps": self._identify_coverage_gaps(categories)
        }
    
    def _categorize_skill(self, skill: Dict) -> str:
        """对 Skill 进行分类"""
        name = skill.get("name", "").lower()
        description = skill.get("description", "").lower()
        text = f"{name} {description}"
        
        if any(kw in text for kw in ["code", "program", "debug", "refactor"]):
            return "programming"
        elif any(kw in text for kw in ["data", "analyze", "query", "database"]):
            return "data_analysis"
        elif any(kw in text for kw in ["doc", "write", "read", "summarize"]):
            return "documentation"
        elif any(kw in text for kw in ["deploy", "docker", "ci", "cd", "build"]):
            return "devops"
        elif any(kw in text for kw in ["test", "unittest", "pytest"]):
            return "testing"
        else:
            return "other"
    
    def _calculate_coverage_score(self, categories: Dict) -> float:
        """计算覆盖度评分 (0-1)"""
        # 理想分布：每个类别至少有 5 个 Skills
        ideal_per_category = 5
        total_ideal = ideal_per_category * len(categories)
        
        actual_total = sum(min(count, ideal_per_category) for count in categories.values())
        
        return round(actual_total / total_ideal, 4)
    
    def _identify_coverage_gaps(self, categories: Dict) -> List[str]:
        """识别覆盖度缺口"""
        gaps = []
        
        for category, count in categories.items():
            if count == 0:
                gaps.append(f"No skills in category: {category}")
            elif count < 3:
                gaps.append(f"Low coverage in {category}: only {count} skills")
        
        return gaps
    
    async def _analyze_usage(self, skills: List[Dict]) -> Dict[str, Any]:
        """分析使用情况"""
        if not skills:
            return {
                "most_used": [],
                "least_used": [],
                "avg_usage_per_skill": 0,
                "unused_skills": 0
            }
        
        # 模拟使用数据（实际应从数据库查询）
        usage_data = []
        for skill in skills:
            usage_count = skill.get("usage_count", 0)
            usage_data.append({
                "skill_id": skill.get("id", skill.get("name")),
                "name": skill.get("name", "unknown"),
                "usage_count": usage_count,
                "last_used": skill.get("last_used_at")
            })
        
        # 排序
        sorted_by_usage = sorted(usage_data, key=lambda x: x["usage_count"], reverse=True)
        
        most_used = sorted_by_usage[:5]
        least_used = sorted([s for s in usage_data if s["usage_count"] > 0], 
                          key=lambda x: x["usage_count"])[:5]
        unused = [s for s in usage_data if s["usage_count"] == 0]
        
        total_usage = sum(s["usage_count"] for s in usage_data)
        avg_usage = total_usage / max(len(usage_data), 1)
        
        return {
            "most_used": most_used,
            "least_used": least_used,
            "unused_skills": len(unused),
            "avg_usage_per_skill": round(avg_usage, 2),
            "total_executions": total_usage
        }
    
    def _evaluate_quality(self, skills: List[Dict]) -> Dict[str, Any]:
        """评估 Skill 质量"""
        if not skills:
            return {
                "avg_quality_score": 0,
                "high_quality_count": 0,
                "low_quality_count": 0,
                "quality_distribution": {}
            }
        
        # 基于多个维度评估质量
        quality_scores = []
        for skill in skills:
            score = self._calculate_skill_quality(skill)
            quality_scores.append(score)
        
        avg_score = sum(quality_scores) / len(quality_scores)
        high_quality = sum(1 for s in quality_scores if s >= 0.8)
        low_quality = sum(1 for s in quality_scores if s < 0.5)
        
        # 质量分布
        distribution = {
            "excellent": sum(1 for s in quality_scores if s >= 0.9),
            "good": sum(1 for s in quality_scores if 0.7 <= s < 0.9),
            "average": sum(1 for s in quality_scores if 0.5 <= s < 0.7),
            "poor": sum(1 for s in quality_scores if s < 0.5)
        }
        
        return {
            "avg_quality_score": round(avg_score, 4),
            "high_quality_count": high_quality,
            "low_quality_count": low_quality,
            "quality_distribution": distribution,
            "needs_improvement": low_quality
        }
    
    def _calculate_skill_quality(self, skill: Dict) -> float:
        """计算单个 Skill 的质量评分"""
        score = 0.5  # 基础分
        
        # 使用频率 (30%)
        usage_count = skill.get("usage_count", 0)
        if usage_count > 100:
            score += 0.3
        elif usage_count > 50:
            score += 0.2
        elif usage_count > 10:
            score += 0.1
        
        # 成功率 (30%)
        success_rate = skill.get("success_rate", 0.5)
        score += success_rate * 0.3
        
        # 用户评分 (20%)
        rating = skill.get("avg_rating", 3)
        score += ((rating - 1) / 4) * 0.2
        
        # 最近更新时间 (20%)
        last_updated = skill.get("last_updated")
        if last_updated:
            # 如果最近 30 天内更新过
            score += 0.2
        
        return min(score, 1.0)
    
    def _identify_opportunities(
        self,
        skills: List[Dict],
        coverage: Dict,
        quality: Dict
    ) -> List[Dict[str, Any]]:
        """识别进化机会"""
        opportunities = []
        
        # 1. 低覆盖度领域的机会
        for gap in coverage.get("gaps", []):
            opportunities.append({
                "type": "new_skill_needed",
                "priority": "high",
                "description": gap,
                "action": "Create new skills to fill coverage gaps"
            })
        
        # 2. 低质量 Skills 的改进机会
        if quality.get("low_quality_count", 0) > 0:
            opportunities.append({
                "type": "skill_improvement",
                "priority": "high",
                "count": quality["low_quality_count"],
                "description": f"{quality['low_quality_count']} skills need quality improvement",
                "action": "Auto-improve or replace low-quality skills"
            })
        
        # 3. 未使用 Skills 的处理
        unused = coverage.get("usage_statistics", {}).get("unused_skills", 0)
        if unused > 0:
            opportunities.append({
                "type": "skill_cleanup",
                "priority": "medium",
                "count": unused,
                "description": f"{unused} unused skills can be removed or improved",
                "action": "Review and cleanup unused skills"
            })
        
        return opportunities
    
    def _generate_recommendations(
        self,
        coverage: Dict,
        quality: Dict,
        opportunities: List[Dict]
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于覆盖度
        if coverage.get("coverage_score", 1) < 0.6:
            recommendations.append(
                "Expand skill coverage in underrepresented categories"
            )
        
        # 基于质量
        if quality.get("avg_quality_score", 1) < 0.7:
            recommendations.append(
                "Focus on improving skill quality through auto-improvement"
            )
        
        # 基于机会
        high_priority = [o for o in opportunities if o.get("priority") == "high"]
        if high_priority:
            recommendations.append(
                f"Address {len(high_priority)} high-priority opportunities"
            )
        
        return recommendations
    
    def get_cached_result(self) -> Optional[Dict]:
        """获取缓存的分析结果"""
        return self.analysis_cache if self.analysis_cache else None
