from typing import List, Dict
from ugc_backend.core.models import ContentPost, Platform
from ugc_backend.ingestion.base import PlatformAdapter
from ugc_backend.ingestion.tiktok import TikTokAdapter
from ugc_backend.ingestion.xiaohongshu import XiaohongshuAdapter


class IngestionManager:
    def __init__(self, adapters: Dict[Platform, PlatformAdapter]):
        self.adapters = adapters

    def discover_posts(
        self,
        platforms: List[Platform],
        keywords: List[str],
        time_window: str = "48h",
    ) -> List[ContentPost]:
        """
        discover posts across multiple platforms
        """
        all_posts = []
        
        for platform in platforms:
            if platform in self.adapters:
                adapter = self.adapters[platform]
                posts = adapter.discover_posts(keywords, time_window)
                all_posts.extend(posts)

        return all_posts

    def monitor_watchlist(
        self,
        platform: Platform,
        creator_ids: List[str],
    ) -> List[ContentPost]:
        """
        monitor specific creators on a platform
        """
        if platform not in self.adapters:
            return []
        
        adapter = self.adapters[platform]
        return adapter.monitor_watchlist(creator_ids)

    def recapture_posts(
        self,
        platform: Platform,
        post_ids: List[str],
    ) -> List[ContentPost]:
        """
        recapture posts to track growth
        """
        if platform not in self.adapters:
            return []
        
        adapter = self.adapters[platform]
        return adapter.recapture_posts(post_ids)
