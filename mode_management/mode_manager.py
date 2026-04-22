"""
模式管理器

管理普通模式和自进化模式的切换
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ModeManager:
    """
    模式管理器
    
    支持两种模式:
    - normal: 普通模式，仅使用 OpenHands + OpenSpace 基础功能
    - evolution: 自进化模式，启用自动进化功能
    """
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            self.config_path = Path(__file__).parent.parent / "config.yaml"
        else:
            self.config_path = Path(config_path)
        
        self.config = self._load_config()
        self.current_mode = self.config.get("mode", "normal")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            # 创建默认配置
            default_config = {
                "mode": "normal",
                "openhands": {
                    "api_url": "http://localhost:3000",
                    "timeout": 300
                },
                "openspace": {
                    "api_url": "http://localhost:8000",
                    "skill_registry": "./skills"
                },
                "evolution": {
                    "interval_hours": 24,
                    "auto_apply": False,
                    "max_concurrent_tests": 3
                }
            }
            self._save_config(default_config)
            return default_config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    def get_current_mode(self) -> str:
        """获取当前模式"""
        return self.current_mode
    
    def set_mode(self, mode: str) -> bool:
        """
        切换模式
        
        Args:
            mode: "normal" 或 "evolution"
        
        Returns:
            是否成功切换
        """
        if mode not in ["normal", "evolution"]:
            raise ValueError(f"Invalid mode: {mode}. Must be 'normal' or 'evolution'")
        
        old_mode = self.current_mode
        self.current_mode = mode
        self.config["mode"] = mode
        self._save_config(self.config)
        
        print(f"✅ Mode switched: {old_mode} → {mode}")
        return True
    
    def is_evolution_mode(self) -> bool:
        """检查是否为自进化模式"""
        return self.current_mode == "evolution"
    
    def is_normal_mode(self) -> bool:
        """检查是否为普通模式"""
        return self.current_mode == "normal"
    
    def get_config(self, key: str = None, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键 (支持点号分隔的嵌套键，如 "evolution.interval_hours")
            default: 默认值
        
        Returns:
            配置值
        """
        if key is None:
            return self.config
        
        # 支持嵌套键访问
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
    
    def update_config(self, key: str, value: Any):
        """
        更新配置项
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split(".")
        config = self.config
        
        # 导航到嵌套字典
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        self._save_config(self.config)
        
        print(f"✅ Config updated: {key} = {value}")
    
    def get_evolution_config(self) -> Dict[str, Any]:
        """获取自进化模式配置"""
        return self.config.get("evolution", {})
    
    def should_run_evolution(self, last_run_time: datetime = None) -> bool:
        """
        检查是否应该运行进化循环
        
        Args:
            last_run_time: 上次运行时间
        
        Returns:
            是否应该运行
        """
        if not self.is_evolution_mode():
            return False
        
        if last_run_time is None:
            return True
        
        interval_hours = self.get_config("evolution.interval_hours", 24)
        hours_since_last_run = (datetime.now() - last_run_time).total_seconds() / 3600
        
        return hours_since_last_run >= interval_hours
    
    def get_mode_info(self) -> Dict[str, Any]:
        """获取模式信息"""
        return {
            "current_mode": self.current_mode,
            "is_evolution": self.is_evolution_mode(),
            "is_normal": self.is_normal_mode(),
            "evolution_config": self.get_evolution_config() if self.is_evolution_mode() else None,
            "config_path": str(self.config_path)
        }
    
    def __repr__(self):
        return f"ModeManager(mode='{self.current_mode}')"


class ConfigLoader:
    """
    配置加载器
    
    支持从多个来源加载配置:
    1. 配置文件 (config.yaml)
    2. 环境变量 (.env)
    3. 命令行参数
    """
    
    def __init__(self, config_path: str = None):
        self.mode_manager = ModeManager(config_path)
    
    def load_all_configs(self) -> Dict[str, Any]:
        """加载所有配置"""
        configs = {
            "mode": self.mode_manager.get_current_mode(),
            "openhands": self.mode_manager.get_config("openhands"),
            "openspace": self.mode_manager.get_config("openspace"),
            "evolution": self.mode_manager.get_config("evolution"),
            "scoring": self.mode_manager.get_config("scoring", {}),
            "ab_testing": self.mode_manager.get_config("ab_testing", {})
        }
        
        # 从环境变量覆盖敏感信息
        import os
        from dotenv import load_dotenv
        
        # 加载 .env 文件
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # 覆盖 API Keys
        if os.getenv("OPENHANDS_API_KEY"):
            configs["openhands"]["api_key"] = os.getenv("OPENHANDS_API_KEY")
        
        if os.getenv("OPENSPACE_API_KEY"):
            configs["openspace"]["api_key"] = os.getenv("OPENSPACE_API_KEY")
        
        if os.getenv("LLM_API_KEY"):
            configs.setdefault("llm", {})["api_key"] = os.getenv("LLM_API_KEY")
        
        return configs
    
    def validate_config(self, configs: Dict[str, Any]) -> list:
        """
        验证配置
        
        Returns:
            错误列表，空列表表示配置有效
        """
        errors = []
        
        # 检查必需的配置
        if not configs.get("openhands", {}).get("api_url"):
            errors.append("OpenHands API URL is required")
        
        if not configs.get("openspace", {}).get("api_url"):
            errors.append("OpenSpace API URL is required")
        
        # 检查自进化模式配置
        if configs.get("mode") == "evolution":
            evolution = configs.get("evolution", {})
            if evolution.get("interval_hours", 0) <= 0:
                errors.append("Evolution interval must be positive")
        
        return errors


if __name__ == "__main__":
    # 测试模式管理器
    manager = ModeManager()
    
    print("=" * 60)
    print("Current Mode Info:")
    print("=" * 60)
    info = manager.get_mode_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("Testing Mode Switch:")
    print("=" * 60)
    
    # 切换到自进化模式
    manager.set_mode("evolution")
    print(f"Is evolution mode: {manager.is_evolution_mode()}")
    
    # 切换回普通模式
    manager.set_mode("normal")
    print(f"Is normal mode: {manager.is_normal_mode()}")
    
    # 测试配置加载器
    print("\n" + "=" * 60)
    print("Config Loader Test:")
    print("=" * 60)
    loader = ConfigLoader()
    configs = loader.load_all_configs()
    print(f"Loaded {len(configs)} config sections")
    
    errors = loader.validate_config(configs)
    if errors:
        print(f"Configuration errors: {errors}")
    else:
        print("✅ Configuration is valid")
