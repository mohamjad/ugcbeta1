from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ugc_backend.api.schemas import (
    BulkIngestRequest,
    IngestResponse,
    DiscoveryRequest,
    DiscoveryResponse,
    ProofTilesResponse,
    ProofTileResponse,
    TrendDetailResponse,
    HealthResponse,
)
from ugc_backend.api.dependencies import get_db
from ugc_backend.core.models import TrendStatus, ContentPost, CreatorProfile, Platform, MarketRegion, ContentType, CreatorTier
from ugc_backend.core.window import WindowManager, WindowType
from ugc_backend.core.cluster import ClusteringEngine
from ugc_backend.core.trend import TrendValidator
from ugc_backend.core.proof_tile import ProofTileGenerator
from ugc_backend.db.repository import PostRepository, ClusterRepository, TrendRepository, ProofTileRepository
from datetime import datetime

router = APIRouter()


@router.post("/api/v1/posts/ingest", response_model=IngestResponse)
def ingest_posts(
    request: BulkIngestRequest,
    db: Session = Depends(get_db),
):
    if not request.posts:
        raise HTTPException(status_code=400, detail="no posts provided")
    
    post_repo = PostRepository(db)
    
    posts = []
    for req_post in request.posts:
        creator = CreatorProfile(
            creator_id=req_post.creator_id,
            username=req_post.creator_username,
            platform=req_post.platform,
            follower_count=req_post.creator_follower_count,
            avg_engagement_rate=0.0,
            follower_growth_rate=0.0,
            tier=CreatorProfile.determine_tier(req_post.creator_follower_count),
            region=req_post.creator_region,
        )
        post = ContentPost(
            post_id=req_post.post_id,
            creator=creator,
            platform=req_post.platform,
            content_type=req_post.content_type,
            caption=req_post.caption,
            hashtags=req_post.hashtags,
            timestamp=req_post.timestamp,
            views=req_post.views,
            likes=req_post.likes,
            comments=req_post.comments,
            shares=req_post.shares,
            saves=req_post.saves,
            first_seen=datetime.now(),
            last_captured=datetime.now(),
            capture_count=1,
        )
        posts.append(post)

    ingested = post_repo.save_posts(posts)
    total = len(posts)

    return IngestResponse(ingested=ingested, total_posts=total)


@router.post("/api/v1/discovery/run", response_model=DiscoveryResponse)
def run_discovery(
    request: DiscoveryRequest,
    db: Session = Depends(get_db),
):
    if not request.platforms:
        raise HTTPException(status_code=400, detail="no platforms specified")
    
    post_repo = PostRepository(db)
    cluster_repo = ClusterRepository(db)
    trend_repo = TrendRepository(db)
    tile_repo = ProofTileRepository(db)
    
    try:
        window_type = WindowType(request.window_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"invalid window_type: {request.window_type}")
    
    window_manager = WindowManager()
    window = window_manager.create_window(window_type)

    db_posts = post_repo.get_posts_by_window(window.start, window.end)
    
    posts = []
    for db_post in db_posts:
        creator = CreatorProfile(
            creator_id=db_post.creator_id,
            username=db_post.creator_username,
            platform=Platform(db_post.platform),
            follower_count=db_post.creator_follower_count,
            avg_engagement_rate=0.0,
            follower_growth_rate=0.0,
            tier=CreatorTier(db_post.creator_tier),
            region=MarketRegion(db_post.creator_region),
        )
        post = ContentPost(
            post_id=db_post.post_id,
            creator=creator,
            platform=Platform(db_post.platform),
            content_type=ContentType(db_post.content_type),
            caption=db_post.caption,
            hashtags=db_post.hashtags or [],
            timestamp=db_post.timestamp,
            views=db_post.views,
            likes=db_post.likes,
            comments=db_post.comments,
            shares=db_post.shares,
            saves=db_post.saves,
            first_seen=db_post.first_seen,
            last_captured=db_post.last_captured,
            capture_count=db_post.capture_count,
        )
        posts.append(post)

    clustering_engine = ClusteringEngine()
    clusters = clustering_engine.cluster_posts(posts)

    validator = TrendValidator()
    validated_count = 0
    tile_ids = []
    tile_generator = ProofTileGenerator()

    for cluster in clusters:
        signal = validator.validate_cluster(cluster, datetime.now())
        
        if signal.validation_confidence >= request.min_confidence:
            cluster_repo.save_cluster(cluster)
            trend_repo.save_trend(signal)
            validated_count += 1

            tile = tile_generator.generate(signal)
            tile_repo.save_tile(tile)
            tile_ids.append(tile.tile_id)

    return DiscoveryResponse(
        clusters_found=len(clusters),
        trends_validated=validated_count,
        proof_tiles_generated=len(tile_ids),
        tile_ids=tile_ids,
    )


@router.get("/api/v1/tiles", response_model=ProofTilesResponse)
def get_proof_tiles(
    status: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    tile_repo = ProofTileRepository(db)
    
    if status:
        db_tiles = tile_repo.get_tiles_by_status(TrendStatus(status))
    elif urgency:
        db_tiles = tile_repo.get_tiles_by_urgency(urgency)
    else:
        db_tiles = tile_repo.get_tiles_by_status(TrendStatus.validated)

    from ugc_backend.api.schemas import TrendMetrics, SuggestedAction
    
    tiles = []
    for db_tile in db_tiles:
        metrics_dict = db_tile.metrics or {}
        metrics = TrendMetrics(
            total_engagement=metrics_dict.get("total_engagement", 0.0),
            growth_rate_24h=metrics_dict.get("growth_rate_24h", 0.0),
            saturation_estimate=metrics_dict.get("saturation_estimate", 0.0),
            creator_replication=metrics_dict.get("creator_replication", 0.0),
            detection_confidence=metrics_dict.get("detection_confidence", 0.0),
            validation_confidence=metrics_dict.get("validation_confidence", 0.0),
            cluster_health=metrics_dict.get("cluster_health", 0.0),
            creator_diversity=metrics_dict.get("creator_diversity", 0.0),
            engagement_strength=metrics_dict.get("engagement_strength", 0.0),
            velocity_score=metrics_dict.get("velocity_score", 0.0),
        )
        
        action_dict = db_tile.suggested_action or {}
        suggested_action = SuggestedAction(
            hashtags=action_dict.get("hashtags", []),
            formats=action_dict.get("formats", []),
            platforms=action_dict.get("platforms", []),
        )
        
        tile = ProofTileResponse(
            tile_id=db_tile.tile_id,
            headline=db_tile.headline,
            urgency=db_tile.urgency,
            recommendation=db_tile.recommendation,
            metrics=metrics,
            suggested_action=suggested_action,
            example_posts=db_tile.example_posts or [],
            creator_samples=db_tile.creator_samples or [],
            status=db_tile.status,
            created_at=db_tile.created_at,
            updated_at=db_tile.updated_at,
        )
        tiles.append(tile)

    return ProofTilesResponse(tiles=tiles)


@router.get("/api/v1/trends/{trend_id}", response_model=TrendDetailResponse)
def get_trend_details(
    trend_id: str,
    db: Session = Depends(get_db),
):
    trend_repo = TrendRepository(db)
    cluster_repo = ClusterRepository(db)
    
    trend = trend_repo.get_trend(trend_id)
    if not trend:
        raise HTTPException(status_code=404, detail="trend not found")

    cluster = cluster_repo.get_cluster(trend.cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="cluster not found")

    from ugc_backend.core.metrics import calculate_saturation_level
    days_active = max((datetime.now() - trend.first_detected).total_seconds() / 86400.0, 1.0)
    saturation = calculate_saturation_level(
        posts=[],
        days_active=days_active,
    )
    if cluster.post_count and days_active > 0:
        saturation = cluster.post_count / days_active

    return TrendDetailResponse(
        trend_id=trend.signal_id,
        cluster_id=trend.cluster_id,
        status=trend.status,
        creator_count=cluster.creator_count,
        post_count=cluster.post_count,
        platforms=cluster.platforms or [],
        regions=cluster.regions or [],
        primary_hashtags=cluster.primary_hashtags or [],
        first_detected=trend.first_detected,
        last_updated=trend.last_updated,
        confidence_scores={
            "detection": cluster.detection_confidence or 0.0,
            "validation": trend.validation_confidence or 0.0,
        },
        growth_metrics={
            "velocity": cluster.velocity_score or 0.0,
            "saturation": saturation,
        },
    )


@router.get("/api/v1/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    from ugc_backend.db.models import PostModel, TrendModel, ProofTileModel
    
    try:
        total_posts = db.query(PostModel).count()
    except:
        total_posts = 0

    try:
        active_trends = db.query(TrendModel).filter(
            TrendModel.status.in_([TrendStatus.validated.value, TrendStatus.validating.value])
        ).count()
    except:
        active_trends = 0

    try:
        tiles_count = db.query(ProofTileModel).filter_by(status=TrendStatus.validated.value).count()
    except:
        tiles_count = 0

    return HealthResponse(
        status="healthy",
        version="1.0",
        components={
            "ingestion": "operational",
            "clustering": "operational",
            "validation": "operational",
            "generation": "operational",
        },
        metrics={
            "total_posts": total_posts,
            "active_clusters": 0,
            "validated_trends": active_trends,
            "proof_tiles": tiles_count,
        },
    )
