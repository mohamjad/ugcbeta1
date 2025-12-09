from abc import ABC, abstractmethod
from typing import List
from ugc_backend.core.models import ContentPost


class PlatformAdapter(ABC):
    @abstractmethod
    def discover_posts(self, keywords: List[str], time_window: str = "48h") -> List[ContentPost]:
        """
        discover posts matching keywords within time window
        """
        pass

    @abstractmethod
    def monitor_watchlist(self, creator_ids: List[str]) -> List[ContentPost]:
        """
        monitor specific creators for new posts
        """
        pass

    @abstractmethod
    def recapture_posts(self, post_ids: List[str]) -> List[ContentPost]:
        """
        re-check posts to measure growth
        """
        pass
