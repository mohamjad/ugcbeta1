from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum
from ugc_backend.core.models import ContentPost


class WindowType(str, Enum):
    early_detection = "early_detection"
    validation = "validation"
    saturation = "saturation"


class TimeWindow:
    def __init__(self, start: datetime, end: datetime, window_type: WindowType):
        self.start = start
        self.end = end
        self.window_type = window_type

    def contains(self, timestamp: datetime) -> bool:
        return self.start <= timestamp <= self.end

    @property
    def duration_hours(self) -> float:
        delta = self.end - self.start
        return delta.total_seconds() / 3600.0

    @classmethod
    def create_early_detection_window(cls, now: datetime, hours: int = 48) -> "TimeWindow":
        return cls(
            start=now - timedelta(hours=hours),
            end=now,
            window_type=WindowType.early_detection,
        )

    @classmethod
    def create_validation_window(cls, now: datetime, hours: int = 168) -> "TimeWindow":
        return cls(
            start=now - timedelta(hours=hours),
            end=now,
            window_type=WindowType.validation,
        )

    @classmethod
    def create_saturation_window(cls, now: datetime, hours: int = 336) -> "TimeWindow":
        return cls(
            start=now - timedelta(hours=hours),
            end=now,
            window_type=WindowType.saturation,
        )


class WindowManager:
    def __init__(self, early_detection_hours: int = 48, validation_hours: int = 168, saturation_hours: int = 336):
        self.early_detection_hours = early_detection_hours
        self.validation_hours = validation_hours
        self.saturation_hours = saturation_hours

    def filter_posts_in_window(self, posts: List[ContentPost], window: TimeWindow) -> List[ContentPost]:
        """
        filter posts within window boundaries
        logs filter rates for transparency
        """
        filtered = [post for post in posts if window.contains(post.timestamp)]
        return filtered

    def create_window(self, window_type: WindowType, now: Optional[datetime] = None) -> TimeWindow:
        if now is None:
            now = datetime.now()
        
        if window_type == WindowType.early_detection:
            return TimeWindow.create_early_detection_window(now, self.early_detection_hours)
        elif window_type == WindowType.validation:
            return TimeWindow.create_validation_window(now, self.validation_hours)
        elif window_type == WindowType.saturation:
            return TimeWindow.create_saturation_window(now, self.saturation_hours)
        else:
            raise ValueError(f"unknown window type: {window_type}")
