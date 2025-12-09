from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from ugc_backend.core.models import Platform, TrendStatus, ContentType, MarketRegion


class PostIngestRequest(BaseModel):
    post_id: str
    platform: Platform
    creator_id: str
    creator_username: str
    creator_follower_count: int = Field(ge=0)
    creator_region: MarketRegion
    content_type: ContentType
    caption: str
    hashtags: List[str] = Field(default_factory=list)
    timestamp: datetime
    views: int = Field(ge=0)
    likes: int = Field(ge=0)
    comments: int = Field(ge=0)
    shares: int = Field(ge=0)
    saves: int = Field(ge=0)


class BulkIngestRequest(BaseModel):
    posts: List[PostIngestRequest]


class IngestResponse(BaseModel):
    ingested: int
    total_posts: int


class DiscoveryRequest(BaseModel):
    window_type: str = "early_detection"
    platforms: List[Platform]
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0)


class DiscoveryResponse(BaseModel):
    clusters_found: int
    trends_validated: int
    proof_tiles_generated: int
    tile_ids: List[str]


class TrendMetrics(BaseModel):
    total_engagement: float
    growth_rate_24h: float
    saturation_estimate: float
    creator_replication: float
    detection_confidence: float
    validation_confidence: float
    cluster_health: float
    creator_diversity: float
    engagement_strength: float
    velocity_score: float


class SuggestedAction(BaseModel):
    hashtags: List[str]
    formats: List[str]
    platforms: List[str]


class ProofTileResponse(BaseModel):
    tile_id: str
    headline: str
    urgency: str
    recommendation: str
    metrics: TrendMetrics
    suggested_action: SuggestedAction
    example_posts: List[Dict]
    creator_samples: List[Dict]
    status: str
    created_at: datetime
    updated_at: datetime


class ProofTilesResponse(BaseModel):
    tiles: List[ProofTileResponse]


class TrendDetailResponse(BaseModel):
    trend_id: str
    cluster_id: str
    status: str
    creator_count: int
    post_count: int
    platforms: List[str]
    regions: List[str]
    primary_hashtags: List[str]
    first_detected: datetime
    last_updated: datetime
    confidence_scores: Dict[str, float]
    growth_metrics: Dict[str, float]


class HealthResponse(BaseModel):
    status: str
    version: str
    components: Dict[str, str]
    metrics: Dict[str, int]
