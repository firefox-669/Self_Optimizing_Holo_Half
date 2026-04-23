"""
LLM 客户端
支持 OpenAI、Anthropic 等主流 LLM API
"""

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LLMClient:
    """
    LLM 客户端
    
    支持多种 LLM 提供商：
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - 其他兼容 OpenAI 格式的 API
    """
    
    def __init__(self, provider: str = None, model: str = None, api_key: str = None):
        """
        初始化 LLM 客户端
        
        Args:
            provider: LLM 提供商 ('openai', 'anthropic', 'custom')
            model: 模型名称
            api_key: API Key（可选，从环境变量读取）
        """
        self.provider = provider or os.getenv('LLM_PROVIDER', 'openai')
        self.model = model or os.getenv('LLM_MODEL', 'gpt-4o-mini')
        self.api_key = api_key or self._get_api_key()
        self.base_url = os.getenv('LLM_BASE_URL', None)
        
        if not self.api_key:
            raise ValueError(
                f"API Key not found for provider '{self.provider}'. "
                f"Please set {self._get_env_var_name()} environment variable."
            )
        
        self.client = self._initialize_client()
    
    def _get_api_key(self) -> Optional[str]:
        """获取 API Key"""
        env_var = self._get_env_var_name()
        return os.getenv(env_var)
    
    def _get_env_var_name(self) -> str:
        """获取环境变量名"""
        if self.provider == 'openai':
            return 'OPENAI_API_KEY'
        elif self.provider == 'anthropic':
            return 'ANTHROPIC_API_KEY'
        else:
            return 'LLM_API_KEY'
    
    def _initialize_client(self):
        """初始化 LLM 客户端"""
        if self.provider == 'openai':
            try:
                from openai import OpenAI
                kwargs = {'api_key': self.api_key}
                if self.base_url:
                    kwargs['base_url'] = self.base_url
                return OpenAI(**kwargs)
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Run: pip install openai"
                )
        
        elif self.provider == 'anthropic':
            try:
                from anthropic import Anthropic
                return Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Anthropic package not installed. Run: pip install anthropic"
                )
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def analyze_info(self, info_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        使用 LLM 分析资讯，生成改进建议
        
        Args:
            info_items: 资讯列表，每个元素包含 title, description, source 等
            
        Returns:
            改进建议列表，每个元素包含：
            - target: 目标系统 ('openhands', 'openspace', 'both')
            - type: 建议类型
            - title: 建议标题
            - description: 详细描述
            - implementation: 实现方案
            - priority: 优先级 (0-10)
            - reasoning: LLM 的推理过程
        """
        if not info_items:
            return []
        
        # 构建 prompt
        prompt = self._build_analysis_prompt(info_items)
        
        # 调用 LLM
        response = await self._call_llm(prompt)
        
        # 解析响应
        suggestions = self._parse_suggestions(response)
        
        return suggestions
    
    def _build_analysis_prompt(self, info_items: List[Dict[str, Any]]) -> str:
        """构建分析提示词"""
        
        # 格式化资讯内容
        info_text = "\n\n".join([
            f"[{i+1}] {item.get('title', 'N/A')}\n"
            f"   Source: {item.get('source', 'N/A')}\n"
            f"   Type: {item.get('type', 'N/A')}\n"
            f"   Date: {item.get('date', 'N/A')}\n"
            f"   URL: {item.get('url', 'N/A')}"
            for i, item in enumerate(info_items[:20])  # 最多分析20条
        ])
        
        prompt = f"""You are an AI agent evolution expert. Analyze the following latest updates about OpenHands, OpenSpace, and AI trends, and generate actionable improvement suggestions for a Self-Evolving AI Agent Platform.

## Latest Updates

{info_text}

## Task

For each relevant update, generate a specific, actionable improvement suggestion that can help the platform evolve. Focus on:

1. **New Features**: Features from OpenHands/OpenSpace that should be integrated
2. **Bug Fixes**: Issues that need to be addressed
3. **Performance Improvements**: Optimization opportunities
4. **Security Enhancements**: Security-related improvements
5. **User Experience**: UX/UI improvements
6. **Integration Opportunities**: Ways to better integrate with other tools

## Output Format

Return a JSON array of suggestions. Each suggestion MUST have these fields:

```json
[
  {{
    "target": "openhands" | "openspace" | "both" | "project",
    "type": "feature_enhancement" | "bug_fix" | "performance" | "security" | "ux_improvement" | "integration",
    "title": "Brief, clear title (max 80 chars)",
    "description": "Detailed explanation of what needs to be done and why",
    "implementation": "Specific steps to implement this suggestion",
    "priority": 1-10 (integer, 10 = highest priority),
    "reasoning": "Why this suggestion is important and how it improves the platform"
  }}
]
```

## Guidelines

- Be specific and actionable
- Prioritize based on impact and feasibility
- Consider both immediate benefits and long-term value
- If an update is not relevant, skip it
- Maximum 10 suggestions total
- Priority should reflect urgency and importance

## Examples

Good suggestion:
{{
  "target": "openhands",
  "type": "feature_enhancement",
  "title": "Add support for multi-file editing",
  "description": "Recent OpenHands update shows improved multi-file handling. Our platform should leverage this capability.",
  "implementation": "1. Update OpenHands client to latest version\n2. Add multi-file test cases\n3. Update documentation",
  "priority": 8,
  "reasoning": "Multi-file editing is essential for complex coding tasks. This will significantly improve user productivity."
}}

Bad suggestion (too vague):
{{
  "title": "Improve performance",
  "description": "Make it faster"
}}

Now analyze the updates and return ONLY the JSON array, no additional text.
"""
        
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        
        if self.provider == 'openai':
            return await self._call_openai(prompt)
        elif self.provider == 'anthropic':
            return await self._call_anthropic(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _call_openai(self, prompt: str) -> str:
        """调用 OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert AI agent evolution analyst. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"❌ OpenAI API call failed: {e}")
            # 返回空结果，不中断流程
            return "[]"
    
    async def _call_anthropic(self, prompt: str) -> str:
        """调用 Anthropic API"""
        try:
            response = self.client.messages.create(
                model=self.model or "claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.7,
                system="You are an expert AI agent evolution analyst. Always respond with valid JSON.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            print(f"❌ Anthropic API call failed: {e}")
            return "[]"
    
    def _parse_suggestions(self, response: str) -> List[Dict[str, Any]]:
        """解析 LLM 响应"""
        import json
        
        try:
            # 尝试解析 JSON
            suggestions = json.loads(response)
            
            # 确保是列表
            if isinstance(suggestions, dict):
                # 如果返回的是对象，尝试提取数组
                suggestions = suggestions.get('suggestions', [])
            
            if not isinstance(suggestions, list):
                print(f"⚠️ Invalid response format: expected list, got {type(suggestions)}")
                return []
            
            # 验证每个建议的字段
            validated = []
            required_fields = ['target', 'type', 'title', 'description', 'implementation', 'priority']
            
            for i, suggestion in enumerate(suggestions):
                if not isinstance(suggestion, dict):
                    continue
                
                # 检查必需字段
                missing = [f for f in required_fields if f not in suggestion]
                if missing:
                    print(f"⚠️ Suggestion {i+1} missing fields: {missing}")
                    continue
                
                # 验证优先级范围
                priority = suggestion.get('priority', 5)
                if not isinstance(priority, (int, float)) or priority < 0 or priority > 10:
                    suggestion['priority'] = 5
                
                # 添加时间戳
                suggestion['generated_at'] = __import__('datetime').datetime.now().isoformat()
                
                validated.append(suggestion)
            
            return validated
        
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse LLM response as JSON: {e}")
            print(f"Response preview: {response[:200]}...")
            return []
    
    async def summarize_analysis(self, suggestions: List[Dict]) -> str:
        """
        使用 LLM 总结分析结果
        
        Args:
            suggestions: 建议列表
            
        Returns:
            总结文本
        """
        if not suggestions:
            return "No suggestions generated."
        
        prompt = f"""Summarize the following {len(suggestions)} improvement suggestions in a concise paragraph (max 200 words).

Suggestions:
{chr(10).join([f"- {s.get('title', '')}: {s.get('description', '')[:100]}" for s in suggestions[:10]])}

Focus on:
1. Main themes or patterns
2. Highest priority items
3. Expected impact

Return only the summary text, no additional formatting.
"""
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                return response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model or "claude-3-sonnet-20240229",
                    max_tokens=500,
                    temperature=0.5,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
        
        except Exception as e:
            print(f"❌ Summarization failed: {e}")
            return f"Generated {len(suggestions)} suggestions across {len(set(s.get('target', '') for s in suggestions))} categories."
