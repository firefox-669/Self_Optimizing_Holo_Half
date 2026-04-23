import asyncio
import aiohttp
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict


class NewsIntegrator:
    """
    AI 前沿信息整合器
    获取真实AI前沿资讯，分析可应用于OpenHands和OpenSpace的改进点
    """

    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(".sohh_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        self._trends: List[Dict] = []
        self._improvements: List[Dict] = []
        self._capabilities: Dict[str, float] = {}
        
        self._last_fetch = None
        self._fetch_interval = 3600
        
        self._load_cache()

    def _load_cache(self):
        """加载缓存"""
        cache_file = self.cache_dir / "ai_trends.json"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._trends = data.get("trends", [])
                self._improvements = data.get("improvements", [])
                self._capabilities = data.get("capabilities", {})

    def _save_cache(self):
        """保存缓存"""
        cache_file = self.cache_dir / "ai_trends.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({
                "trends": self._trends,
                "improvements": self._improvements,
                "capabilities": self._capabilities,
                "updated": datetime.now().isoformat(),
            }, f, indent=2, ensure_ascii=False)

    async def fetch_latest(self) -> List[Dict]:
        """
        获取最新AI前沿资讯
        """
        if self._last_fetch:
            elapsed = (datetime.now() - self._last_fetch).total_seconds()
            if elapsed < self._fetch_interval:
                return self._trends
        
        try:
            trends = await self._fetch_real_trends()
            self._trends = trends
            self._last_fetch = datetime.now()
            self._save_cache()
        except Exception as e:
            print(f"Fetch trends error: {e}")
            self._trends = []
        
        return self._trends

    async def _fetch_real_trends(self) -> List[Dict]:
        """
        从多个真实来源获取AI趋势
        """
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
                "url": "https://news.google.com/rss/search?q=AI+code+generation&hl=en-US&gl=US&ceid=US:en",
                "category": "AI Code Generation",
            },
            {
                "url": "https://news.google.com/rss/search?q=multi-agent+AI+collaboration&hl=en-US&gl=US&ceid=US:en",
                "category": "Multi-Agent Collaboration",
            },
            {
                "url": "https://news.google.com/rss/search?q=AI+safety+monitoring&hl=en-US&gl=US&ceid=US:en",
                "category": "AI Safety",
            },
        ]
        
        async with aiohttp.ClientSession() as session:
            for source in sources:
                try:
                    async with session.get(
                        source["url"],
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            items = self._parse_rss(text, source["category"])
                            trends.extend(items)
                except Exception:
                    pass
        
        if not trends:
            await self._fetch_from_github(trends)
        
        return trends[:20]

    def _parse_rss(self, xml: str, category: str) -> List[Dict]:
        """解析RSS"""
        items = []
        import re
        titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', xml)
        for title in titles[:5]:
            items.append({
                "title": title.strip(),
                "category": category,
                "source": "google_news",
                "detected_at": datetime.now().isoformat(),
            })
        return items

    async def _fetch_from_github(self, trends: List[Dict]):
        """从GitHub trending获取"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://api.github.com/search/repositories?q=AI+agent+stars:>100",
                    headers={"Accept": "application/vnd.github.v3+json"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for repo in data.get("items", [])[:5]:
                            trends.append({
                                "title": repo.get("full_name", ""),
                                "description": repo.get("description", ""),
                                "category": "GitHub Trending",
                                "stars": repo.get("stargazers_count", 0),
                                "source": "github",
                                "detected_at": datetime.now().isoformat(),
                            })
            except Exception:
                pass

    def analyze_improvements(self) -> List[Dict]:
        """
        分析可应用于OpenHands和OpenSpace的改进点
        """
        improvements = []
        
        for trend in self._trends:
            category = trend.get("category", "")
            title = trend.get("title", "")
            
            if "openhands" in title.lower() or "openhands" in category.lower():
                improvements.append({
                    "target": "openhands",
                    "improvement": title,
                    "category": category,
                    "priority": self._calculate_priority(trend),
                })
            elif "openspace" in title.lower() or "openspace" in category.lower():
                improvements.append({
                    "target": "openspace",
                    "improvement": title,
                    "category": category,
                    "priority": self._calculate_priority(trend),
                })
            elif "self-evolution" in title.lower() or "evolution" in category.lower():
                improvements.append({
                    "target": "both",
                    "improvement": title,
                    "category": category,
                    "priority": self._calculate_priority(trend),
                })
            elif "agent" in title.lower() or "agent" in category.lower():
                improvements.append({
                    "target": "both",
                    "improvement": title,
                    "category": category,
                    "priority": self._calculate_priority(trend),
                })
        
        improvements.sort(key=lambda x: x.get("priority", 0), reverse=True)
        self._improvements = improvements
        return improvements

    def _calculate_priority(self, trend: Dict) -> float:
        """计算优先级"""
        priority = 0.5
        
        stars = trend.get("stars", 0)
        if stars > 1000:
            priority += 0.3
        elif stars > 100:
            priority += 0.2
        
        source = trend.get("source", "")
        if source == "github":
            priority += 0.2
        
        return min(1.0, priority)

    def get_improvements(self) -> List[Dict]:
        """获取改进点"""
        return self._improvements

    async def close(self):
        """关闭"""
        self._save_cache()