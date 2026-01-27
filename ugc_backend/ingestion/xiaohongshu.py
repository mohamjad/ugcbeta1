from typing import List, Optional
from datetime import datetime
from ugc_backend.core.models import (
    ContentPost,
    CreatorProfile,
    Platform,
    ContentType,
    MarketRegion,
    CreatorTier,
)
from ugc_backend.ingestion.base import PlatformAdapter


class XiaohongshuAdapter(PlatformAdapter):
    def __init__(self, scraper_enabled: bool = True, rate_limit: int = 60):
        self.scraper_enabled = scraper_enabled
        self.rate_limit = rate_limit

    def discover_posts(self, keywords: List[str], time_window: str = "48h") -> List[ContentPost]:
        """
        scrape posts from xiaohongshu matching keywords
        note: in production, use proper scraping with rate limiting and legal compliance
        """
        posts = []
        
        if not self.scraper_enabled:
            return posts

        for keyword in keywords:
            try:
                scraped_data = self._scrape_search_results(keyword)
                for item in scraped_data:
                    post = self._convert_to_content_post(item)
                    if post:
                        posts.append(post)
            except Exception:
                continue

        return posts

    def monitor_watchlist(self, creator_ids: List[str]) -> List[ContentPost]:
        posts = []
        
        for creator_id in creator_ids:
            try:
                scraped_data = self._scrape_creator_posts(creator_id)
                for item in scraped_data:
                    post = self._convert_to_content_post(item)
                    if post:
                        posts.append(post)
            except Exception:
                continue

        return posts

    def recapture_posts(self, post_ids: List[str]) -> List[ContentPost]:
        posts = []
        
        for post_id in post_ids:
            try:
                item = self._scrape_post_details(post_id)
                post = self._convert_to_content_post(item)
                if post:
                    post.capture_count += 1
                    post.last_captured = datetime.now()
                    posts.append(post)
            except Exception:
                continue

        return posts

    def _scrape_search_results(self, keyword: str) -> List[dict]:
        """
        placeholder for actual scraping implementation
        in production, use selenium/playwright with proper headers and rate limiting
        """
        return []

    def _scrape_creator_posts(self, creator_id: str) -> List[dict]:
        return []

    def _scrape_post_details(self, post_id: str) -> dict:
        return {}

    def _convert_to_content_post(self, item: dict) -> Optional[ContentPost]:
        if not item:
            return None

        try:
            author = item.get("author", {})
            follower_count = author.get("follower_count", 0)
            
            creator = CreatorProfile(
                creator_id=author.get("id", ""),
                username=author.get("username", ""),
                platform=Platform.xiaohongshu,
                follower_count=follower_count,
                avg_engagement_rate=author.get("avg_engagement_rate", 0.0),
                follower_growth_rate=0.0,
                tier=CreatorProfile.determine_tier(follower_count),
                region=MarketRegion.china,
            )

            hashtags = self._extract_hashtags(item.get("description", ""))
            timestamp = self._parse_timestamp(item.get("create_time"))

            return ContentPost(
                post_id=item.get("id", ""),
                creator=creator,
                platform=Platform.xiaohongshu,
                content_type=self._determine_content_type(item),
                caption=item.get("description", ""),
                hashtags=hashtags,
                timestamp=timestamp,
                views=item.get("views", 0),
                likes=item.get("likes", 0),
                comments=item.get("comments", 0),
                shares=item.get("shares", 0),
                saves=item.get("saves", 0),
                first_seen=datetime.now(),
                last_captured=datetime.now(),
                capture_count=1,
            )
        except Exception:
            return None

    def _extract_hashtags(self, text: str) -> List[str]:
        import re
        hashtags = re.findall(r"#(\w+)", text)
        return [tag.lower() for tag in hashtags]

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except Exception:
            return datetime.now()

    def _determine_content_type(self, item: dict) -> ContentType:
        media_type = item.get("media_type", "image")
        if media_type == "video":
            return ContentType.video
        elif media_type == "carousel":
            return ContentType.carousel
        else:
            return ContentType.image
