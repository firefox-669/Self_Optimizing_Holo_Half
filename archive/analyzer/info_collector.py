"""
资讯驱动分析器
从 GitHub/News 抓取 OpenHands/OpenSpace/AI 前沿动态
用于发现现有能力的改进点和扩展方向
"""

import asyncio
import aiohttp
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict


class InfoCollector:
    """
    资讯驱动分析器
    从多个来源抓取最新动态，分析可改进点
    """
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(".sohh_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        self._openhands_info: List[Dict] = []
        self._openspace_info: List[Dict] = []
        self._ai_trends: List[Dict] = []
        self._improvements: List[Dict] = []
        
        self._last_fetch = None
        self._fetch_interval = 3600  # 1小时
        
        self._load_cache()
    
    def _load_cache(self):
        """加载缓存"""
        cache_file = self.cache_dir / "info_collector.json"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._openhands_info = data.get("openhands_info", [])
                self._openspace_info = data.get("openspace_info", [])
                self._ai_trends = data.get("ai_trends", [])
                self._improvements = data.get("improvements", [])
    
    def _save_cache(self):
        """保存缓存"""
        cache_file = self.cache_dir / "info_collector.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({
                "openhands_info": self._openhands_info,
                "openspace_info": self._openspace_info,
                "ai_trends": self._ai_trends,
                "improvements": self._improvements,
                "updated": datetime.now().isoformat(),
            }, f, indent=2, ensure_ascii=False)
    
    async def collect_all(self) -> Dict[str, List[Dict]]:
        """收集所有资讯"""
        if self._last_fetch:
            elapsed = (datetime.now() - self._last_fetch).total_seconds()
            if elapsed < self._fetch_interval:
                return {
                    "openhands": self._openhands_info,
                    "openspace": self._openspace_info,
                    "ai_trends": self._ai_trends,
                }
        
        # 并行抓取所有来源
        results = await asyncio.gather(
            self._collect_openhands(),
            self._collect_openspace(),
            self._collect_ai_trends(),
            return_exceptions=True
        )
        
        self._openhands_info = results[0] if not isinstance(results[0], Exception) else []
        self._openspace_info = results[1] if not isinstance(results[1], Exception) else []
        self._ai_trends = results[2] if not isinstance(results[2], Exception) else []
        
        # 处理异常情况
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Collection {i} failed: {result}")
        
        self._last_fetch = datetime.now()
        self._save_cache()
        
        return {
            "openhands": self._openhands_info,
            "openspace": self._openspace_info,
            "ai_trends": self._ai_trends,
        }
    
    async def _collect_openhands(self) -> List[Dict]:
        """收集 OpenHands 最新动态"""
        info = []
        
        sources = [
            {
                "url": "https://api.github.com/repos/All-Hands-AI/OpenHands/commits?per_page=10",
                "type": "commits",
            },
            {
                "url": "https://api.github.com/repos/All-Hands-AI/OpenHands/releases?per_page=5",
                "type": "releases",
            },
            {
                "url": "https://api.github.com/repos/All-Hands-AI/OpenHands/pulls?state=closed&per_page=10",
                "type": "pulls",
            },
            {
                "url": "https://api.github.com/repos/All-Hands-AI/OpenHands/issues?state=open&per_page=5",
                "type": "issues",
            },
        ]
        
        async with aiohttp.ClientSession() as session:
            for source in sources:
                try:
                    async with session.get(
                        source["url"],
                        headers={"Accept": "application/vnd.github.v3+json"},
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            items = data if isinstance(data, list) else []
                            
                            for item in items[:5]:
                                info.append({
                                    "source": "openhands",
                                    "type": source["type"],
                                    "title": item.get("name") or item.get("title", ""),
                                    "sha": item.get("sha", "")[:7],
                                    "url": item.get("html_url", ""),
                                    "date": item.get("created_at") or item.get("commit", {}).get("author", {}).get("date", ""),
                                    "author": item.get("user", {}).get("login", "") if isinstance(item, dict) else "",
                                    "detected_at": datetime.now().isoformat(),
                                })
                except Exception as e:
                    print(f"Failed to fetch OpenHands {source['type']}: {e}")
        
        return info
    
    async def _collect_openspace(self) -> List[Dict]:
        """收集 OpenSpace 最新动态"""
        info = []
        
        sources = [
            {
                "url": "https://api.github.com/repos/HKUDS/OpenSpace/commits?per_page=10",
                "type": "commits",
            },
            {
                "url": "https://api.github.com/repos/HKUDS/OpenSpace/releases?per_page=5",
                "type": "releases",
            },
            {
                "url": "https://api.github.com/repos/HKUDS/OpenSpace/pulls?state=closed&per_page=10",
                "type": "pulls",
            },
            {
                "url": "https://api.github.com/repos/HKUDS/OpenSpace/releases",
                "type": "release_notes",
            },
        ]
        
        async with aiohttp.ClientSession() as session:
            for source in sources:
                try:
                    async with session.get(
                        source["url"],
                        headers={"Accept": "application/vnd.github.v3+json"},
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            items = data if isinstance(data, list) else []
                            
                            for item in items[:5]:
                                info.append({
                                    "source": "openspace",
                                    "type": source["type"],
                                    "title": item.get("name") or item.get("title", ""),
                                    "sha": item.get("sha", "")[:7],
                                    "url": item.get("html_url", ""),
                                    "date": item.get("created_at") or item.get("commit", {}).get("author", {}).get("date", ""),
                                    "author": item.get("user", {}).get("login", "") if isinstance(item, dict) else "",
                                    "detected_at": datetime.now().isoformat(),
                                })
                except Exception as e:
                    print(f"Failed to fetch OpenSpace {source['type']}: {e}")
        
        return info
    
    async def _collect_ai_trends(self) -> List[Dict]:
        """收集 AI Agent 前沿趋势"""
        trends = []
        
        sources = [
            {
                "url": "https://news.google.com/rss/search?q=AI+agent+self-evolution&hl=en-US&gl=US&ceid=US:en",
                "category": "AI Agent Self-Evolution",
            },
            {
                "url": "https://news.google.com/rss/search?q=autonomous+coding+AI&hl=en-US&gl=US&ceid=US:en",
                "category": "Autonomous Coding",
            },
            {
                "url": "https://news.google.com/rss/search?q=multi-agent+AI+collaboration&hl=en-US&gl=US&ceid=US:en",
                "category": "Multi-Agent",
            },
            {
                "url": "https://api.github.com/search/repositories?q=AI+agent+stars:>100&per_page=10",
                "category": "GitHub Trending",
            },
        ]
        
        async with aiohttp.ClientSession() as session:
            for source in sources:
                try:
                    if "api.github.com" in source["url"]:
                        async with session.get(
                            source["url"],
                            headers={"Accept": "application/vnd.github.v3+json"},
                            timeout=aiohttp.ClientTimeout(total=10),
                        ) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                for repo in data.get("items", [])[:5]:
                                    trends.append({
                                        "source": "ai_trends",
                                        "type": "repo",
                                        "category": source["category"],
                                        "title": repo.get("full_name", ""),
                                        "description": repo.get("description", ""),
                                        "stars": repo.get("stargazers_count", 0),
                                        "url": repo.get("html_url", ""),
                                        "detected_at": datetime.now().isoformat(),
                                    })
                    else:
                        async with session.get(
                            source["url"],
                            timeout=aiohttp.ClientTimeout(total=10),
                        ) as resp:
                            if resp.status == 200:
                                text = await resp.text()
                                items = self._parse_rss(text, source["category"])
                                trends.extend(items)
                except Exception as e:
                    print(f"Failed to fetch AI trends: {e}")
        
        return trends
    
    def _parse_rss(self, xml: str, category: str) -> List[Dict]:
        """解析 RSS"""
        items = []
        import re
        try:
            titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', xml)
            for title in titles[:5]:
                items.append({
                    "source": "ai_trends",
                    "type": "news",
                    "category": category,
                    "title": title.strip(),
                    "detected_at": datetime.now().isoformat(),
                })
        except:
            pass
        return items
    
    def analyze_improvements(self) -> List[Dict]:
        """
        分析可改进点
        基于资讯分析现有能力可以改进或扩展的方向
        """
        improvements = []
        
        # 分析 OpenHands 改进点
        for info in self._openhands_info:
            info_type = info.get("type", "")
            title = info.get("title", "")
            
            # 从 commit message 分析改进方向
            if info_type == "commits":
                improvements.append({
                    "target": "openhands",
                    "type": "feature_enhancement",
                    "improvement": title,
                    "source_info": info,
                    "category": "execution",
                    "priority": self._calculate_priority(info),
                })
            
            # 从 PR 分析新功能
            elif info_type == "pulls":
                improvements.append({
                    "target": "openhands",
                    "type": "new_feature",
                    "improvement": title,
                    "source_info": info,
                    "category": "extension",
                    "priority": self._calculate_priority(info),
                })
        
        # 分析 OpenSpace 改进点
        for info in self._openspace_info:
            info_type = info.get("type", "")
            title = info.get("title", "")
            
            if info_type == "commits":
                improvements.append({
                    "target": "openspace",
                    "type": "feature_enhancement",
                    "improvement": title,
                    "source_info": info,
                    "category": "evolution",
                    "priority": self._calculate_priority(info),
                })
            elif info_type == "releases":
                improvements.append({
                    "target": "openspace",
                    "type": "version_update",
                    "improvement": title,
                    "source_info": info,
                    "category": "upgrade",
                    "priority": self._calculate_priority(info),
                })
        
        # 分析 AI 趋势
        for trend in self._ai_trends:
            category = trend.get("category", "")
            title = trend.get("title", "")
            
            # 相关的 AI Agent 趋势
            if "agent" in title.lower() or "agent" in category.lower():
                improvements.append({
                    "target": "both",
                    "type": "new_capability",
                    "improvement": title,
                    "source_info": trend,
                    "category": "extension",
                    "priority": self._calculate_priority(trend),
                })
        
        # 按优先级排序
        improvements.sort(key=lambda x: x.get("priority", 0), reverse=True)
        self._improvements = improvements
        return improvements
    
    def _calculate_priority(self, info: Dict) -> float:
        """计算优先级"""
        priority = 0.5
        
        # GitHub stars 加权
        stars = info.get("stars", 0)
        if stars > 1000:
            priority += 0.3
        elif stars > 100:
            priority += 0.2
        
        # 来源加权
        source = info.get("source", "")
        if source == "openhands" or source == "openspace":
            priority += 0.2
        elif source == "ai_trends":
            priority += 0.1
        
        # 类型加权
        info_type = info.get("type", "")
        if info_type == "releases":
            priority += 0.2
        elif info_type == "commits":
            priority += 0.1
        
        return min(1.0, priority)
    
    def generate_suggestions(self) -> List[Dict]:
        """生成 Evolution Suggestions"""
        return [
            {
                "id": f"suggestion_{i}",
                "target": imp.get("target", ""),
                "type": imp.get("type", ""),
                "title": imp.get("improvement", "")[:100],
                "description": f"基于 {imp.get('source_info', {}).get('source', 'unknown')} 发现",
                "source_info": imp.get("source_info", {}),
                "category": imp.get("category", ""),
                "priority": imp.get("priority", 0.5),
                "status": "pending",
            }
            for i, imp in enumerate(self._improvements)
        ]
    
    def get_openhands_info(self) -> List[Dict]:
        """获取 OpenHands 资讯"""
        return self._openhands_info
    
    def get_openspace_info(self) -> List[Dict]:
        """获取 OpenSpace 资讯"""
        return self._openspace_info
    
    def get_ai_trends(self) -> List[Dict]:
        """获取 AI 趋势"""
        return self._ai_trends
    
    def get_improvements(self) -> List[Dict]:
        """获取改进点"""
        return self._improvements
    
    async def close(self):
        """关闭"""
        self._save_cache()