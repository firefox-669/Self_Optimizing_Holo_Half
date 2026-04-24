"""
项目自身分析器
分析项目自身的代码结构、模块完整性、测试覆盖等
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
import ast
import json


class ProjectSelfAnalyzer:
    """
    项目自身分析器
    分析项目代码结构、能力健康度
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path(__file__).parent.parent
        self._analysis_cache: Dict[str, Any] = {}
        self._modules: List[Dict] = []
    
    async def analyze(self) -> Dict[str, Any]:
        """全面分析项目自身"""
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "modules": self._analyze_modules(),
            "code_structure": self._analyze_code_structure(),
            "capabilities": self._analyze_capabilities(),
            "health_metrics": self._analyze_health(),
            "integrations": self._analyze_integrations(),
            "test_coverage": self._analyze_test_coverage(),
        }
        
        self._analysis_cache = analysis
        return analysis
    
    def _analyze_modules(self) -> List[Dict]:
        """分析模块结构"""
        modules = []
        
        # 核心模块
        core_dirs = [
            "core",
            "executor",
            "evolution",
            "monitor",
            "ai_news",
            "patches",
            "evaluation",
            "integrations",
            "analyzer",
            "reporting",
            "version_control",
            "optimizer",
        ]
        
        for dir_name in core_dirs:
            dir_path = self.project_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                py_files = list(dir_path.glob("*.py"))
                py_files = [f for f in py_files if f.name not in ["__init__.py", "__pycache__"]]
                
                modules.append({
                    "name": dir_name,
                    "path": str(dir_path),
                    "files": len(py_files),
                    "exists": True,
                })
        
        self._modules = modules
        return modules
    
    def _analyze_code_structure(self) -> Dict[str, Any]:
        """分析代码结构"""
        structure = {
            "total_files": 0,
            "total_lines": 0,
            "by_module": {},
        }
        
        for module in self._modules:
            module_name = module["name"]
            module_path = self.project_path / module_name
            
            file_count = 0
            line_count = 0
            
            for py_file in module_path.glob("**/*.py"):
                if "__pycache__" in str(py_file):
                    continue
                
                try:
                    content = py_file.read_text(encoding="utf-8")
                    lines = len(content.split("\n"))
                    file_count += 1
                    line_count += lines
                except:
                    pass
            
            structure["by_module"][module_name] = {
                "files": file_count,
                "lines": line_count,
            }
            structure["total_files"] += file_count
            structure["total_lines"] += line_count
        
        return structure
    
    def _analyze_capabilities(self) -> Dict[str, float]:
        """分析能力评分"""
        scores = {}
        
        # 执行能力
        scores["execution"] = self._evaluate_execution()
        
        # 进化能力
        scores["evolution"] = self._evaluate_evolution()
        
        # 安全能力
        scores["safety"] = self._evaluate_safety()
        
        # 集成能力
        scores["integration"] = self._evaluate_integration()
        
        # 自分析能力
        scores["self_analysis"] = self._evaluate_self_analysis()
        
        # 计算总分
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        scores["overall"] = round(overall, 3)
        
        return scores
    
    def _evaluate_execution(self) -> float:
        """评估执行能力"""
        score = 0.3
        
        # 检查 executor 模块
        if (self.project_path / "executor").exists():
            score += 0.2
        
        executor_file = self.project_path / "executor" / "executor.py"
        if executor_file.exists():
            content = executor_file.read_text(encoding="utf-8")
            if "async def execute" in content:
                score += 0.2
            if "OpenHands" in content:
                score += 0.2
            if "async def" in content:
                score += 0.1
        
        return min(1.0, score)
    
    def _evaluate_evolution(self) -> float:
        """评估进化能力"""
        score = 0.3
        
        if (self.project_path / "evolution").exists():
            score += 0.2
        
        evolver_file = self.project_path / "evolution" / "evolver.py"
        if evolver_file.exists():
            content = evolver_file.read_text(encoding="utf-8")
            if "async def evolve" in content:
                score += 0.2
            if "self_modify" in content or "evolve" in content:
                score += 0.2
        
        return min(1.0, score)
    
    def _evaluate_safety(self) -> float:
        """评估安全能力"""
        score = 0.4
        
        if (self.project_path / "monitor").exists():
            score += 0.2
        
        safety_file = self.project_path / "monitor" / "safety.py"
        if safety_file.exists():
            content = safety_file.read_text(encoding="utf-8")
            if "dangerous" in content or "security" in content:
                score += 0.2
            if "max_" in content:
                score += 0.1
        
        return min(1.0, score)
    
    def _evaluate_integration(self) -> float:
        """评估集成能力"""
        score = 0.4
        
        if (self.project_path / "integrations").exists():
            score += 0.3
        
        # 检查是否有 OpenHands/OpenSpace 集成
        for module in self._modules:
            if "openhand" in module["name"].lower() or "openspace" in module["name"].lower():
                score += 0.2
        
        return min(1.0, score)
    
    def _evaluate_self_analysis(self) -> float:
        """评估自分析能力"""
        score = 0.3
        
        if (self.project_path / "analyzer").exists():
            score += 0.3
        
        analyzer_file = self.project_path / "analyzer" / "openhands_analyzer.py"
        if analyzer_file.exists():
            score += 0.2
        
        info_collector = self.project_path / "analyzer" / "info_collector.py"
        if info_collector.exists():
            score += 0.2
        
        return min(1.0, score)
    
    def _analyze_health(self) -> Dict[str, Any]:
        """分析健康指标"""
        return {
            "last_analysis": self._analysis_cache.get("timestamp", ""),
            "modules_count": len(self._modules),
            "has_readme": (self.project_path / "README.md").exists(),
            "has_requirements": (self.project_path / "requirements.txt").exists(),
            "has_tests": (self.project_path / "tests").exists() if (self.project_path / "tests").exists() else False,
            "has_.plan": (self.project_path / "IMPLEMENTATION_PLAN.md").exists(),
        }
    
    def _analyze_integrations(self) -> Dict[str, Any]:
        """分析集成的外部服务"""
        integrations = {
            "openhands": False,
            "openspace": False,
        }
        
        # 检查 integrations 目录
        integrations_dir = self.project_path / "integrations"
        if integrations_dir.exists():
            if (integrations_dir / "openhands").exists():
                integrations["openhands"] = True
            if (integrations_dir / "openspace").exists():
                integrations["openspace"] = True
        
        return integrations
    
    def _analyze_test_coverage(self) -> Dict[str, Any]:
        """分析测试覆盖"""
        tests_dir = self.project_path / "tests"
        
        if not tests_dir.exists():
            return {
                "exists": False,
                "test_files": 0,
                "coverage": 0.0,
            }
        
        test_files = list(tests_dir.glob("test_*.py"))
        
        return {
            "exists": True,
            "test_files": len(test_files),
            "coverage": min(1.0, len(test_files) / 10),  # 估计覆盖率
        }
    
    def get_cached_analysis(self) -> Dict[str, Any]:
        """获取缓存的分析结果"""
        return self._analysis_cache
    
    def get_suggestions(self) -> List[Dict]:
        """生成改进建议"""
        suggestions = []
        
        capabilities = self._analysis_cache.get("capabilities", {})
        
        # 基于能力评分生成建议
        for capability, score in capabilities.items():
            if capability == "overall":
                continue
            
            if score < 0.6:
                suggestions.append({
                    "id": f"self_improve_{capability}",
                    "target": "project",
                    "type": "capability_enhancement",
                    "title": f"提升 {capability} 能力",
                    "description": f"当前 {capability} 能力评分: {score}",
                    "priority": 1.0 - score,
                    "status": "pending",
                })
        
        # 基于健康指标
        health = self._analysis_cache.get("health_metrics", {})
        if not health.get("has_tests"):
            suggestions.append({
                "id": "self_add_tests",
                "target": "project",
                "type": "test_coverage",
                "title": "添加测试",
                "description": "项目缺少测试文件",
                "priority": 0.5,
                "status": "pending",
            })
        
        suggestions.sort(key=lambda x: x.get("priority", 0), reverse=True)
        return suggestions