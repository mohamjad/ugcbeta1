from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Platform(str, Enum):
    tiktok = "tiktok"
    xiaohongshu = "xiaohongshu"
    rednote = "rednote"
    douyin = "douyin"
    instagram = "instagram"


class ContentType(str, Enum):
    video = "video"
    image = "image"
    text = "text"
    carousel = "carousel"


class MarketRegion(str, Enum):
    us = "us"
    uk = "uk"
    china = "china"
    japan = "japan"
    korea = "korea"
    global_ = "global"


class TrendStatus(str, Enum):
    emerging = "emerging"
    validating = "validating"
    validated = "validated"
    saturated = "saturated"
    declining = "declining"


class CreatorTier(str, Enum):
    nano = "nano"  # < 10k
    micro = "micro"  # 10k - 100k
    mid = "mid"  # 100k - 1m
    macro = "macro"  # 1m+


class CreatorProfile(BaseModel):
    creator_id: str
    username: str
    platform: Platform
    follower_count: int = Field(ge=0)
    avg_engagement_rate: float = Field(ge=0.0, le=1.0)
    follower_growth_rate: float = Field(default=0.0)
    tier: CreatorTier
    region: MarketRegion

    @property
    def is_mid_tier(self) -> bool:
        return self.tier == CreatorTier.mid

    @classmethod
    def determine_tier(cls, follower_count: int) -> CreatorTier:
        if follower_count < 10_000:
            return CreatorTier.nano
        elif follower_count < 100_000:
            return CreatorTier.micro
        elif follower_count < 1_000_000:
            return CreatorTier.mid
        else:
            return CreatorTier.macro


class ContentPost(BaseModel):
    post_id: str
    creator: CreatorProfile
    platform: Platform
    content_type: ContentType
    caption: str
    hashtags: List[str] = Field(default_factory=list)
    timestamp: datetime
    views: int = Field(ge=0)
    likes: int = Field(ge=0)
    comments: int = Field(ge=0)
    shares: int = Field(ge=0)
    saves: int = Field(ge=0)
    first_seen: datetime
    last_captured: datetime
    capture_count: int = Field(default=1, ge=1)

    @field_validator("hashtags", mode="before")
    @classmethod
    def normalize_hashtags(cls, v):
        if isinstance(v, str):
            return [tag.strip("#").lower() for tag in v.split() if tag.startswith("#")]
        return [tag.strip("#").lower() if isinstance(tag, str) else str(tag).lower() for tag in v]

    @property
    def total_engagement(self) -> int:
        return self.likes + self.comments + self.shares + self.saves

    @property
    def engagement_rate(self) -> float:
        if self.views == 0:
            return 0.0
        return (self.likes + self.comments + self.shares) / self.views

    @property
    def hours_since_first_seen(self) -> float:
        delta = datetime.now() - self.first_seen
        return delta.total_seconds() / 3600.0

    @property
    def velocity(self) -> float:
        hours = self.hours_since_first_seen
        if hours == 0:
            return 0.0
        return self.total_engagement / hours
