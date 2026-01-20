from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ugc_backend.core.models import ContentPost, TrendStatus
from ugc_backend.core.cluster import Cluster
from ugc_backend.core.trend import TrendSignal
from ugc_backend.core.proof_tile import ProofTile
from ugc_backend.db.models import (
    PostModel,
    ClusterModel,
    TrendModel,
    ProofTileModel,
)


class PostRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_posts(self, posts: List[ContentPost]) -> int:
        if not posts:
            return 0
        
        saved_count = 0
        try:
            for post in posts:
                existing = self.session.query(PostModel).filter_by(post_id=post.post_id).first()
                if existing:
                    self._update_post_model(existing, post)
                else:
                    model = self._post_to_model(post)
                    self.session.add(model)
                    saved_count += 1
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise
        return saved_count

    def get_posts_by_window(self, start: datetime, end: datetime) -> List[PostModel]:
        return (
            self.session.query(PostModel)
            .filter(PostModel.timestamp >= start, PostModel.timestamp <= end)
            .all()
        )

    def get_posts_by_ids(self, post_ids: List[str]) -> List[PostModel]:
        return self.session.query(PostModel).filter(PostModel.post_id.in_(post_ids)).all()

    def _post_to_model(self, post: ContentPost) -> PostModel:
        return PostModel(
            post_id=post.post_id,
            creator_id=post.creator.creator_id,
            creator_username=post.creator.username,
            creator_follower_count=post.creator.follower_count,
            creator_tier=post.creator.tier.value,
            creator_region=post.creator.region.value,
            platform=post.platform.value,
            content_type=post.content_type.value,
            caption=post.caption,
            hashtags=post.hashtags,
            timestamp=post.timestamp,
            views=post.views,
            likes=post.likes,
            comments=post.comments,
            shares=post.shares,
            saves=post.saves,
            first_seen=post.first_seen,
            last_captured=post.last_captured,
            capture_count=post.capture_count,
        )

    def _update_post_model(self, model: PostModel, post: ContentPost):
        model.views = post.views
        model.likes = post.likes
        model.comments = post.comments
        model.shares = post.shares
        model.saves = post.saves
        model.last_captured = post.last_captured
        model.capture_count = post.capture_count


class ClusterRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_cluster(self, cluster: Cluster) -> ClusterModel:
        health = cluster.calculate_health()
        model = ClusterModel(
            cluster_id=cluster.cluster_id,
            primary_hashtags=cluster.primary_hashtags,
            post_ids=[post.post_id for post in cluster.posts],
            platforms=list(cluster.platforms),
            regions=list(cluster.regions),
            health_score=health.health_score,
            creator_diversity=health.creator_diversity,
            engagement_strength=health.engagement_strength,
            velocity_score=health.velocity_score,
            detection_confidence=health.detection_confidence,
            post_count=len(cluster.posts),
            creator_count=len(cluster.unique_creators),
        )
        self.session.add(model)
        self.session.commit()
        return model

    def get_cluster(self, cluster_id: str) -> Optional[ClusterModel]:
        return self.session.query(ClusterModel).filter_by(cluster_id=cluster_id).first()


class TrendRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_trend(self, signal: TrendSignal) -> TrendModel:
        model = TrendModel(
            signal_id=signal.signal_id,
            cluster_id=signal.cluster.cluster_id,
            status=signal.status.value,
            first_detected=signal.first_detected,
            last_updated=signal.last_updated,
            validation_confidence=signal.validation_confidence,
        )
        self.session.add(model)
        self.session.commit()
        return model

    def get_trend(self, signal_id: str) -> Optional[TrendModel]:
        return self.session.query(TrendModel).filter_by(signal_id=signal_id).first()

    def get_trends_by_status(self, status: TrendStatus) -> List[TrendModel]:
        return self.session.query(TrendModel).filter_by(status=status.value).all()

    def get_active_trends(self) -> List[TrendModel]:
        return (
            self.session.query(TrendModel)
            .filter(
                TrendModel.status.in_([
                    TrendStatus.validated.value,
                    TrendStatus.validating.value,
                ])
            )
            .order_by(TrendModel.validation_confidence.desc())
            .all()
        )


class ProofTileRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_tile(self, tile: ProofTile) -> ProofTileModel:
        model = ProofTileModel(
            tile_id=tile.tile_id,
            trend_id=tile.trend_id,
            headline=tile.headline,
            urgency=tile.urgency.value,
            recommendation=tile.recommendation,
            status=tile.status.value,
            metrics=tile.metrics,
            suggested_action=tile.suggested_action,
            example_posts=tile.example_posts,
            creator_samples=tile.creator_samples,
        )
        self.session.add(model)
        self.session.commit()
        return model

    def get_tile(self, tile_id: str) -> Optional[ProofTileModel]:
        return self.session.query(ProofTileModel).filter_by(tile_id=tile_id).first()

    def get_tiles_by_status(self, status: TrendStatus) -> List[ProofTileModel]:
        return self.session.query(ProofTileModel).filter_by(status=status.value).all()

    def get_tiles_by_urgency(self, urgency: str) -> List[ProofTileModel]:
        return self.session.query(ProofTileModel).filter_by(urgency=urgency).all()
