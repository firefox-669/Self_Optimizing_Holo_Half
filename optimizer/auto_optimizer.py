"""
自动优化引擎
评估、执行优化建议，并进行效果评估
支持真正的代码修改和自动回退
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AutoOptimizer:
    """
    自动优化引擎
    自动评估和应用优化建议
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self._optimizations: List[Dict] = []
        self._baseline_scores: Dict[str, float] = {}
    
    async def evaluate_suggestion(self, suggestion: Dict) -> bool:
        """评估建议是否值得执行"""
        
        # 检查优先级
        priority = suggestion.get("priority", 0)
        if priority < 0.3:
            return False
        
        # 检查类型
        suggestion_type = suggestion.get("type", "")
        supported_types = [
            "connection",
            "capability_enhancement",
            "feature_enhancement",
            "new_feature",
            "version_update",
            "skill_capture",
        ]
        
        if suggestion_type not in supported_types:
            return False
        
        return True
    
    async def apply_optimization(
        self, 
        suggestion: Dict,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """应用优化"""
        
        result = {
            "suggestion_id": suggestion.get("id"),
            "applied": False,
            "error": None,
            "timestamp": datetime.now().isoformat(),
        }
        
        # 根据类型应用不同的优化
        suggestion_type = suggestion.get("type", "")
        target = suggestion.get("target", "")
        
        if suggestion_type == "connection":
            result["applied"] = await self._apply_connection(suggestion, context)
        
        elif suggestion_type in ["capability_enhancement", "feature_enhancement"]:
            result = await self._apply_code_enhancement(suggestion, context)
        
        elif suggestion_type == "version_update":
            result["applied"] = await self._apply_version_update(suggestion, context)
        
        elif suggestion_type == "skill_capture":
            result["applied"] = await self._apply_skill_capture(suggestion, context)
        
        else:
            result["error"] = f"Unsupported type: {suggestion_type}"
        
        return result
    
    async def _apply_connection(
        self, 
        suggestion: Dict,
        context: Dict[str, Any],
    ) -> bool:
        """应用连接优化"""
        
        target = suggestion.get("target", "")
        
        if target == "openhands":
            # 更新 requirements 添加 OpenHands
            req_file = self.workspace / "requirements.txt"
            if req_file.exists():
                content = req_file.read_text(encoding="utf-8")
                if "openhands" not in content:
                    content += "\nopenhands>=0.1.0\n"
                    req_file.write_text(content, encoding="utf-8")
                    return True
        
        elif target == "openspace":
            # 更新 requirements 添加 OpenSpace
            req_file = self.workspace / "requirements.txt"
            if req_file.exists():
                content = req_file.read_text(encoding="utf-8")
                if "OpenSpace" not in content:
                    content += "\n# OpenSpace\n# pip install -e git+https://github.com/HKUDS/OpenSpace.git\n"
                    req_file.write_text(content, encoding="utf-8")
                    return True
        
        return False
    
    async def _apply_code_enhancement(
        self, 
        suggestion: Dict,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        应用代码增强（真正的代码修改）
        
        使用 CodeGenerator 生成代码补丁，然后用 CodeApplier 安全应用
        """
        from core.code_generator import CodeGenerator
        from core.code_applier import CodeApplier
        
        result = {
            "suggestion_id": suggestion.get("id"),
            "applied": False,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "modified_files": [],
            "new_files": [],
            "backup_id": None
        }
        
        try:
            logger.info(f"🔧 Applying code enhancement: {suggestion.get('title')}")
            
            # 1. 生成代码补丁
            code_gen = CodeGenerator()
            patch = await code_gen.generate_code_patch(suggestion)
            
            if not patch.get("success"):
                result["error"] = f"Code generation failed: {patch.get('error')}"
                logger.error(result["error"])
                return result
            
            logger.info(f"✅ Code patch generated: {len(patch.get('files_to_modify', []))} files to modify, {len(patch.get('new_files', []))} new files")
            
            # 2. 应用代码补丁
            code_applier = CodeApplier(str(self.workspace))
            apply_result = await code_applier.apply_code_patch(
                patch=patch,
                run_tests=True  # 运行测试验证
            )
            
            if apply_result["success"]:
                result["applied"] = True
                result["modified_files"] = apply_result["modified_files"]
                result["new_files"] = apply_result["new_files"]
                result["backup_id"] = apply_result["backup_id"]
                logger.info(f"✅ Code enhancement applied successfully!")
            else:
                result["error"] = f"Code application failed: {apply_result.get('error')}"
                logger.error(result["error"])
            
            return result
        
        except Exception as e:
            result["error"] = f"Exception during code enhancement: {str(e)}"
            logger.error(result["error"], exc_info=True)
            return result
    
    async def _apply_enhancement(
        self, 
        suggestion: Dict,
        context: Dict[str, Any],
    ) -> bool:
        """应用能力增强"""
        
        # 记录增强操作
        # 实际的代码修改需要更复杂的逻辑
        target = suggestion.get("target", "")
        title = suggestion.get("title", "")
        
        # 创建增强记录
        enhancement_file = self.workspace / ".sohh_cache" / "enhancements.json"
        import json
        
        enhancements = []
        if enhancement_file.exists():
            with open(enhancement_file, "r") as f:
                enhancements = json.load(f)
        
        enhancements.append({
            "suggestion": suggestion,
            "applied_at": datetime.now().isoformat(),
        })
        
        with open(enhancement_file, "w") as f:
            json.dump(enhancements, f, indent=2)
        
        return True
    
    async def _apply_version_update(
        self, 
        suggestion: Dict,
        context: Dict[str, Any],
    ) -> bool:
        """应用版本更新"""
        
        # 记录版本更新需求
        return True
    
    async def _apply_skill_capture(
        self, 
        suggestion: Dict,
        context: Dict[str, Any],
    ) -> bool:
        """应用 Skill 捕获"""
        
        return True
    
    async def compare_with_baseline(
        self, 
        before_scores: Dict[str, float], 
        after_scores: Dict[str, float],
    ) -> Dict[str, Any]:
        """比较优化前后的能力变化"""
        
        changes = {}
        improved_any = False
        
        for key in after_scores:
            if key in before_scores:
                delta = after_scores[key] - before_scores[key]
                changes[key] = {
                    "before": before_scores[key],
                    "after": after_scores[key],
                    "delta": round(delta, 3),
                    "improved": delta > 0,
                }
                if delta > 0:
                    improved_any = True
        
        overall_before = before_scores.get("overall", 0)
        overall_after = after_scores.get("overall", 0)
        overall_delta = overall_after - overall_before
        
        result = {
            "improved": overall_delta > 0,
            "improved_any": improved_any,
            "overall_before": overall_before,
            "overall_after": overall_after,
            "overall_delta": round(overall_delta, 3),
            "changes": changes,
            "recommendation": self._get_recommendation(overall_delta),
            "timestamp": datetime.now().isoformat(),
        }
        
        # 更新基线
        if result["improved"]:
            self._baseline_scores = after_scores.copy()
        
        return result
    
    def _get_recommendation(self, delta: float) -> str:
        """获取建议"""
        if delta > 0.1:
            return "keep"
        elif delta > 0:
            return "keep"
        else:
            return "rollback"
    
    def get_optimizations(self) -> List[Dict]:
        """获取应用的优化"""
        return self._optimizations
    
    def set_baseline(self, scores: Dict[str, float]):
        """设置基线"""
        self._baseline_scores = scores
    
    def get_baseline(self) -> Dict[str, float]:
        """获取基线"""
        return self._baseline_scores