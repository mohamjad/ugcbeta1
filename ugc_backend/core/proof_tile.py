from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum
from pydantic import BaseModel
from ugc_backend.core.models import ContentPost, TrendStatus
from ugc_backend.core.trend import TrendSignal


class UrgencyLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ProofTile(BaseModel):
    tile_id: str
    headline: str
    urgency: UrgencyLevel
    recommendation: str
    trend_id: str
    status: TrendStatus
    
    metrics: Dict[str, float]
    suggested_action: Dict[str, List[str]]
    example_posts: List[Dict]
    creator_samples: List[Dict]
    
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


class ProofTileGenerator:
    def __init__(self, urgency_threshold: float = 0.8):
        self.urgency_threshold = urgency_threshold

    def generate(self, signal: TrendSignal) -> ProofTile:
        """
        transform validated trend into actionable proof tile
        includes complete evidence and transparent metrics
        """
        posts = signal.cluster.posts
        health = signal.cluster.calculate_health()

        urgency, recommendation = self._calculate_urgency(signal)
        
        headline = self._generate_headline(signal)
        
        metrics = self._calculate_metrics(signal, posts, health)
        
        suggested_action = self._generate_suggestions(signal)
        
        example_posts = self._select_example_posts(posts)
        
        creator_samples = self._select_creator_samples(posts)

        tile_id = f"tile_{signal.signal_id}"
        
        return ProofTile(
            tile_id=tile_id,
            headline=headline,
            urgency=urgency,
            recommendation=recommendation,
            trend_id=signal.signal_id,
            status=signal.status,
            metrics=metrics,
            suggested_action=suggested_action,
            example_posts=example_posts,
            creator_samples=creator_samples,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def _calculate_urgency(self, signal: TrendSignal) -> Tuple[UrgencyLevel, str]:
        """
        urgency calculation:
        - high: validated status + confidence >0.8 -> act now
        - medium: validating status -> prepare
        - low: emerging/monitor -> continue tracking
        """
        if signal.status == TrendStatus.validated and signal.validation_confidence >= self.urgency_threshold:
            return UrgencyLevel.high, "act now: create content within 48h"
        elif signal.status == TrendStatus.validating:
            return UrgencyLevel.medium, "prepare: develop concepts"
        elif signal.status == TrendStatus.validated:
            return UrgencyLevel.medium, "prepare: develop concepts"
        else:
            return UrgencyLevel.low, "monitor: continue tracking"

    def _generate_headline(self, signal: TrendSignal) -> str:
        hashtags_str = ", ".join(signal.primary_hashtags[:3])
        return f"emerging trend: {hashtags_str} - {signal.creator_replication_count} creators, {signal.post_count} posts"

    def _calculate_metrics(
        self,
        signal: TrendSignal,
        posts: List[ContentPost],
        health,
    ) -> Dict[str, float]:
        total_engagement = sum(post.total_engagement for post in posts)
        
        from ugc_backend.core.metrics import calculate_velocity_score, calculate_saturation_level
        velocities = [calculate_velocity_score(post) for post in posts]
        avg_velocity = sum(velocities) / len(velocities) if velocities else 0.0
        
        hours_active = (datetime.now() - signal.first_detected).total_seconds() / 3600.0
        days_active = max(hours_active / 24.0, 1.0)
        saturation = calculate_saturation_level(posts, days_active)
        
        growth_rate_24h = avg_velocity * 24.0

        return {
            "total_engagement": float(total_engagement),
            "growth_rate_24h": growth_rate_24h,
            "saturation_estimate": saturation,
            "creator_replication": float(signal.creator_replication_count),
            "detection_confidence": health.detection_confidence,
            "validation_confidence": signal.validation_confidence,
            "cluster_health": health.health_score,
            "creator_diversity": health.creator_diversity,
            "engagement_strength": health.engagement_strength,
            "velocity_score": health.velocity_score,
        }

    def _generate_suggestions(self, signal: TrendSignal) -> Dict[str, List[str]]:
        hashtags = signal.primary_hashtags[:5]
        
        content_types = list(set(post.content_type.value for post in signal.cluster.posts))
        
        platforms = [p.value for p in signal.platforms]

        return {
            "hashtags": hashtags,
            "formats": content_types,
            "platforms": platforms,
        }

    def _select_example_posts(self, posts: List[ContentPost], limit: int = 5) -> List[Dict]:
        sorted_posts = sorted(
            posts,
            key=lambda p: p.total_engagement,
            reverse=True,
        )[:limit]

        return [
            {
                "post_id": post.post_id,
                "platform": post.platform.value,
                "caption": post.caption[:200],
                "hashtags": post.hashtags,
                "engagement": post.total_engagement,
                "views": post.views,
                "likes": post.likes,
                "comments": post.comments,
                "shares": post.shares,
                "timestamp": post.timestamp.isoformat(),
            }
            for post in sorted_posts
        ]

    def _select_creator_samples(self, posts: List[ContentPost], limit: int = 5) -> List[Dict]:
        creator_map = {}
        for post in posts:
            creator_id = post.creator.creator_id
            if creator_id not in creator_map:
                creator_map[creator_id] = {
                    "creator_id": creator_id,
                    "username": post.creator.username,
                    "platform": post.creator.platform.value,
                    "follower_count": post.creator.follower_count,
                    "tier": post.creator.tier.value,
                    "region": post.creator.region.value,
                    "post_count": 0,
                    "total_engagement": 0,
                }
            creator_map[creator_id]["post_count"] += 1
            creator_map[creator_id]["total_engagement"] += post.total_engagement

        creators = sorted(
            creator_map.values(),
            key=lambda c: c["total_engagement"],
            reverse=True,
        )[:limit]

        return creators
