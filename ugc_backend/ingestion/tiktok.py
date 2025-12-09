from typing import List, Optional
import httpx
from datetime import datetime, timedelta
from ugc_backend.core.models import (
    ContentPost,
    CreatorProfile,
    Platform,
    ContentType,
    MarketRegion,
    CreatorTier,
)
from ugc_backend.ingestion.base import PlatformAdapter


class TikTokAdapter(PlatformAdapter):
    def __init__(self, api_key: Optional[str] = None, rate_limit: int = 100):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.base_url = "https://api.tiktok.com/v1"

    def discover_posts(self, keywords: List[str], time_window: str = "48h") -> List[ContentPost]:
        """
        fetch posts from tiktok api matching keywords
        converts to normalized contentpost format
        """
        posts = []
        
        for keyword in keywords:
            try:
                response = self._api_request(
                    "hashtag/posts",
                    params={"hashtag": keyword, "count": 100},
                )
                
                for item in response.get("data", []):
                    post = self._convert_to_content_post(item)
                    if post:
                        posts.append(post)
            except Exception as e:
                continue

        return posts

    def monitor_watchlist(self, creator_ids: List[str]) -> List[ContentPost]:
        posts = []
        
        for creator_id in creator_ids:
            try:
                response = self._api_request(
                    f"user/{creator_id}/posts",
                    params={"count": 50},
                )
                
                for item in response.get("data", []):
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
                response = self._api_request(f"post/{post_id}")
                post = self._convert_to_content_post(response.get("data"))
                if post:
                    post.capture_count += 1
                    post.last_captured = datetime.now()
                    posts.append(post)
            except Exception:
                continue

        return posts

    def _api_request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        with httpx.Client() as client:
            response = client.get(url, headers=headers, params=params or {}, timeout=10.0)
            response.raise_for_status()
            return response.json()

    def _convert_to_content_post(self, item: dict) -> Optional[ContentPost]:
        if not item:
            return None

        try:
            author = item.get("author", {})
            stats = item.get("statistics", {})
            
            follower_count = author.get("follower_count", 0)
            creator = CreatorProfile(
                creator_id=author.get("id", ""),
                username=author.get("username", ""),
                platform=Platform.tiktok,
                follower_count=follower_count,
                avg_engagement_rate=self._calculate_engagement_rate(author),
                follower_growth_rate=0.0,
                tier=CreatorProfile.determine_tier(follower_count),
                region=MarketRegion.us,
            )

            hashtags = self._extract_hashtags(item.get("description", ""))
            timestamp = datetime.fromtimestamp(item.get("create_time", 0))

            return ContentPost(
                post_id=item.get("id", ""),
                creator=creator,
                platform=Platform.tiktok,
                content_type=ContentType.video,
                caption=item.get("description", ""),
                hashtags=hashtags,
                timestamp=timestamp,
                views=stats.get("play_count", 0),
                likes=stats.get("digg_count", 0),
                comments=stats.get("comment_count", 0),
                shares=stats.get("share_count", 0),
                saves=stats.get("collect_count", 0),
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

    def _calculate_engagement_rate(self, author: dict) -> float:
        return author.get("avg_engagement_rate", 0.0)
