"""
自定义评分规则管理器
允许用户自定义评分权重、阈值和规则
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class CustomScoringRules:
    """
    自定义评分规则管理器
    
    支持：
    1. 自定义权重
    2. 自定义阈值
    3. 自定义规则（条件判断）
    4. 禁用某些维度
    """
    
    def __init__(self, workspace: str = None, config_file: str = "config_scoring_custom.yaml"):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.config_file = self.workspace / config_file
        
        # 默认配置
        self.default_weights = {
            "success_rate": 0.25,
            "efficiency": 0.20,
            "user_satisfaction": 0.20,
            "skill_effectiveness": 0.15,
            "error_handling": 0.10,
            "integration": 0.10,
        }
        
        self.default_thresholds = {
            "efficiency": {
                "excellent": 60,   # < 60秒 = 优秀
                "poor": 300,       # > 300秒 = 差
            },
            "satisfaction": {
                "max_iterations": 50,  # 超过 50 次迭代满意度最低
            },
            "min_acceptable_score": 0.6,  # 最低接受分数
        }
        
        # 加载的配置
        self.enabled = False
        self.custom_weights = {}
        self.custom_thresholds = {}
        self.custom_rules = []
        self.disabled_dimensions = []
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """加载自定义配置"""
        if not self.config_file.exists():
            logger.info(f"📝 No custom scoring config found at {self.config_file}")
            logger.info("💡 Copy config_scoring_custom.yaml.example to config_scoring_custom.yaml to customize")
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                logger.warning("⚠️  Empty config file")
                return
            
            # 是否启用
            self.enabled = config.get('enabled', False)
            
            if not self.enabled:
                logger.info("⚙️  Custom scoring rules disabled")
                return
            
            # 加载自定义权重
            if 'custom_weights' in config:
                self.custom_weights = config['custom_weights']
                self._validate_weights()
                logger.info(f"✅ Loaded custom weights: {list(self.custom_weights.keys())}")
            
            # 加载自定义阈值
            if 'thresholds' in config:
                self.custom_thresholds = config['thresholds']
                logger.info(f"✅ Loaded custom thresholds")
            
            # 加载自定义规则
            if 'custom_rules' in config:
                self.custom_rules = config['custom_rules']
                logger.info(f"✅ Loaded {len(self.custom_rules)} custom rules")
            
            # 加载禁用的维度
            if 'disabled_dimensions' in config:
                self.disabled_dimensions = config['disabled_dimensions']
                logger.info(f"✅ Disabled dimensions: {self.disabled_dimensions}")
            
            logger.info("✅ Custom scoring rules loaded successfully")
        
        except Exception as e:
            logger.error(f"❌ Failed to load custom scoring config: {e}")
            logger.warning("⚠️  Falling back to default scoring rules")
    
    def _validate_weights(self):
        """验证权重总和是否为 1.0"""
        # 合并默认权重和自定义权重
        merged_weights = self.default_weights.copy()
        merged_weights.update(self.custom_weights)
        
        # 移除禁用的维度
        for dim in self.disabled_dimensions:
            merged_weights.pop(dim, None)
        
        total = sum(merged_weights.values())
        
        if abs(total - 1.0) > 0.01:
            logger.warning(f"⚠️  Weights sum to {total}, not 1.0. Normalizing...")
            # 自动归一化
            for key in merged_weights:
                merged_weights[key] = merged_weights[key] / total
            
            self.custom_weights = {
                k: v for k, v in merged_weights.items() 
                if k not in self.default_weights or abs(v - self.default_weights[k]) > 0.001
            }
    
    def get_weights(self) -> Dict[str, float]:
        """获取最终权重（合并默认和自定义）"""
        if not self.enabled:
            return self.default_weights
        
        weights = self.default_weights.copy()
        weights.update(self.custom_weights)
        
        # 移除禁用的维度
        for dim in self.disabled_dimensions:
            weights.pop(dim, None)
        
        return weights
    
    def get_threshold(self, dimension: str, threshold_name: str, default_value=None):
        """获取自定义阈值"""
        if not self.enabled:
            return default_value
        
        return (
            self.custom_thresholds
            .get(dimension, {})
            .get(threshold_name, default_value)
        )
    
    def apply_custom_rules(self, scores: Dict[str, float], total_score: float) -> float:
        """
        应用自定义规则调整总分
        
        Args:
            scores: 各维度评分
            total_score: 原始总分
            
        Returns:
            调整后的总分
        """
        if not self.enabled or not self.custom_rules:
            return total_score
        
        adjusted_score = total_score
        
        for rule in self.custom_rules:
            try:
                condition = rule.get('condition', '')
                action = rule.get('action', '')
                
                # 评估条件
                if self._evaluate_condition(condition, scores):
                    # 执行动作
                    adjusted_score = self._execute_action(action, adjusted_score, scores)
                    logger.info(f"✅ Rule '{rule.get('name')}' applied: {rule.get('description')}")
            
            except Exception as e:
                logger.warning(f"⚠️  Failed to apply rule '{rule.get('name')}': {e}")
        
        # 确保分数在 0-1 之间
        return max(0.0, min(1.0, adjusted_score))
    
    def _evaluate_condition(self, condition: str, scores: Dict[str, float]) -> bool:
        """
        评估条件表达式
        
        支持的语法：
        - success_rate < 0.5
        - efficiency > 0.9 and user_satisfaction > 0.8
        - skill_effectiveness == 1.0
        """
        try:
            # 构建安全的命名空间
            safe_dict = {
                key: value for key, value in scores.items()
                if key in ['success_rate', 'efficiency', 'user_satisfaction', 
                          'skill_effectiveness', 'error_handling', 'integration']
            }
            
            # 使用 eval 评估（在安全上下文中）
            result = eval(condition, {"__builtins__": {}}, safe_dict)
            return bool(result)
        
        except Exception as e:
            logger.warning(f"⚠️  Condition evaluation failed: {condition} - {e}")
            return False
    
    def _execute_action(self, action: str, current_score: float, scores: Dict[str, float]) -> float:
        """
        执行规则动作
        
        支持的动作：
        - multiply_total_by_X: 总分乘以 X
        - add_X_to_total: 总分加 X
        - set_total_to_X: 总分设为 X
        """
        if action.startswith('multiply_total_by_'):
            multiplier = float(action.split('_')[-1])
            return current_score * multiplier
        
        elif action.startswith('add_') and action.endswith('_to_total'):
            value = float(action.split('_')[1])
            return current_score + value
        
        elif action.startswith('set_total_to_'):
            value = float(action.split('_')[-1])
            return value
        
        else:
            logger.warning(f"⚠️  Unknown action: {action}")
            return current_score
    
    def is_dimension_enabled(self, dimension: str) -> bool:
        """检查维度是否启用"""
        return dimension not in self.disabled_dimensions
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "enabled": self.enabled,
            "custom_weights": self.custom_weights if self.enabled else {},
            "custom_rules_count": len(self.custom_rules) if self.enabled else 0,
            "disabled_dimensions": self.disabled_dimensions if self.enabled else [],
        }
