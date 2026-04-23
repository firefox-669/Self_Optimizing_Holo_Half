"""
代码生成器
使用 LLM 生成 Python 代码补丁，实现真正的自进化
"""

import os
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()


class CodeGenerator:
    """
    代码生成器
    
    根据改进建议，自动生成 Python 代码补丁
    """
    
    def __init__(self, llm_client=None):
        """
        初始化代码生成器
        
        Args:
            llm_client: LLM 客户端实例（可选，会自动创建）
        """
        if llm_client is None:
            from core.llm_client import LLMClient
            self.llm = LLMClient()
        else:
            self.llm = llm_client
        
        self.workspace = Path.cwd()
    
    async def generate_code_patch(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据建议生成代码补丁
        
        Args:
            suggestion: 改进建议字典
            
        Returns:
            包含代码补丁的字典：
            {
                "success": bool,
                "files_to_modify": [...],
                "patches": [...],
                "new_files": [...],
                "reasoning": str
            }
        """
        target = suggestion.get('target', '')
        suggestion_type = suggestion.get('type', '')
        title = suggestion.get('title', '')
        description = suggestion.get('description', '')
        implementation = suggestion.get('implementation', '')
        
        # 构建 prompt
        prompt = self._build_code_generation_prompt(
            target, suggestion_type, title, description, implementation
        )
        
        # 调用 LLM 生成代码
        response = await self.llm._call_llm(prompt)
        
        # 解析响应
        try:
            import json
            result = json.loads(response)
            
            # 验证结果格式
            if not self._validate_patch(result):
                return {
                    "success": False,
                    "error": "Invalid patch format",
                    "raw_response": response
                }
            
            return {
                "success": True,
                "files_to_modify": result.get("files_to_modify", []),
                "patches": result.get("patches", []),
                "new_files": result.get("new_files", []),
                "reasoning": result.get("reasoning", ""),
                "suggestion_id": suggestion.get("id")
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse LLM response: {e}",
                "raw_response": response
            }
    
    def _build_code_generation_prompt(
        self,
        target: str,
        suggestion_type: str,
        title: str,
        description: str,
        implementation: str
    ) -> str:
        """构建代码生成 prompt"""
        
        # 获取项目结构信息
        project_structure = self._get_project_structure()
        
        prompt = f"""You are an expert Python developer tasked with implementing a code improvement for the Self_Optimizing_Holo_Half project.

## Improvement Suggestion

**Target**: {target}
**Type**: {suggestion_type}
**Title**: {title}
**Description**: {description}
**Implementation Guide**: {implementation}

## Project Structure

{project_structure}

## Task

Generate the exact code changes needed to implement this improvement. You can:
1. Modify existing files within the Self_Optimizing_Holo_Half directory
2. Create new files within the Self_Optimizing_Holo_Half directory
3. Delete files (if necessary)

## IMPORTANT SAFETY RULES

⚠️ **DO NOT modify external projects like OpenHands or OpenSpace**
⚠️ **ONLY modify files within the Self_Optimizing_Holo_Half workspace**
⚠️ **All file paths must be relative to the SOHH project root**

## Output Format

Return a JSON object with this structure:

```json
{{
  "files_to_modify": [
    {{
      "file_path": "relative/path/to/file.py",
      "operation": "modify",
      "changes": [
        {{
          "line_start": 10,
          "line_end": 15,
          "new_code": "replacement code here"
        }}
      ]
    }}
  ],
  "new_files": [
    {{
      "file_path": "relative/path/to/new_file.py",
      "content": "full file content here"
    }}
  ],
  "reasoning": "Explanation of why these changes implement the suggestion"
}}
```

## Important Rules

1. **Safety First**: 
   - Do NOT break existing functionality
   - Add proper error handling
   - Include type hints
   
2. **Code Quality**:
   - Follow PEP 8 style guide
   - Add docstrings to new functions
   - Use meaningful variable names
   
3. **Testing**:
   - If adding new features, suggest test cases
   - Ensure backward compatibility
   
4. **File Paths**:
   - Use relative paths from project root (Self_Optimizing_Holo_Half/)
   - Verify file exists before modifying
   - NEVER use absolute paths
   - NEVER reference paths outside the workspace
   
5. **Completeness**:
   - Provide FULL file content for new files
   - For modifications, show EXACT line ranges

## Example

Good response:
```json
{{
  "files_to_modify": [
    {{
      "file_path": "evolution/suggestion_engine.py",
      "operation": "modify",
      "changes": [
        {{
          "line_start": 50,
          "line_end": 60,
          "new_code": "    async def generate_suggestions(...):\n        # New implementation\n        pass"
        }}
      ]
    }}
  ],
  "new_files": [],
  "reasoning": "This change adds LLM-based analysis to improve suggestion quality"
}}
```

Now generate the code changes for the improvement suggestion above. Return ONLY valid JSON, no additional text.
"""
        
        return prompt
    
    def _get_project_structure(self, max_depth=3) -> str:
        """获取项目结构"""
        structure = []
        
        for path in sorted(self.workspace.rglob("*")):
            # 跳过隐藏文件和缓存
            if any(part.startswith('.') or part == '__pycache__' 
                   for part in path.parts):
                continue
            
            # 只包含 Python 文件和关键配置
            if path.is_file() and path.suffix in ['.py', '.yaml', '.yml', '.md']:
                rel_path = path.relative_to(self.workspace)
                
                # 限制深度
                if len(rel_path.parts) <= max_depth:
                    indent = "  " * (len(rel_path.parts) - 1)
                    structure.append(f"{indent}{path.name}")
        
        return "\n".join(structure[:50])  # 最多50行
    
    def _validate_patch(self, patch: Dict) -> bool:
        """验证补丁格式"""
        # 检查必需字段
        if "files_to_modify" not in patch and "new_files" not in patch:
            return False
        
        # 验证文件修改
        for file_mod in patch.get("files_to_modify", []):
            if "file_path" not in file_mod:
                return False
            if "operation" not in file_mod:
                return False
        
        # 验证新文件
        for new_file in patch.get("new_files", []):
            if "file_path" not in new_file:
                return False
            if "content" not in new_file:
                return False
        
        return True
    
    async def generate_multiple_patches(
        self, 
        suggestions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        为多个建议生成代码补丁
        
        Args:
            suggestions: 建议列表
            
        Returns:
            补丁列表
        """
        patches = []
        
        for i, suggestion in enumerate(suggestions):
            print(f"Generating patch {i+1}/{len(suggestions)}: {suggestion.get('title', 'N/A')}")
            
            patch = await self.generate_code_patch(suggestion)
            patches.append(patch)
        
        return patches
