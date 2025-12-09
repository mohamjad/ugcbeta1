from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PostModel(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(255), unique=True, nullable=False, index=True)
    creator_id = Column(String(255), nullable=False, index=True)
    creator_username = Column(String(255))
    creator_follower_count = Column(Integer, default=0)
    creator_tier = Column(String(50))
    creator_region = Column(String(50))
    platform = Column(String(50), nullable=False, index=True)
    content_type = Column(String(50))
    caption = Column(String(5000))
    hashtags = Column(JSON)
    timestamp = Column(DateTime, nullable=False, index=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    first_seen = Column(DateTime, nullable=False)
    last_captured = Column(DateTime, nullable=False)
    capture_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index("idx_post_timestamp", "timestamp"),
        Index("idx_post_platform_timestamp", "platform", "timestamp"),
    )


class ClusterModel(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(String(255), unique=True, nullable=False, index=True)
    primary_hashtags = Column(JSON)
    post_ids = Column(JSON)
    platforms = Column(JSON)
    regions = Column(JSON)
    health_score = Column(Float)
    creator_diversity = Column(Float)
    engagement_strength = Column(Float)
    velocity_score = Column(Float)
    detection_confidence = Column(Float)
    post_count = Column(Integer)
    creator_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class TrendModel(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(String(255), unique=True, nullable=False, index=True)
    cluster_id = Column(String(255), ForeignKey("clusters.cluster_id"), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    first_detected = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    validation_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    cluster = relationship("ClusterModel", backref="trends")


class ProofTileModel(Base):
    __tablename__ = "proof_tiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tile_id = Column(String(255), unique=True, nullable=False, index=True)
    trend_id = Column(String(255), ForeignKey("trends.signal_id"), nullable=False)
    headline = Column(String(500))
    urgency = Column(String(50), index=True)
    recommendation = Column(String(500))
    status = Column(String(50))
    metrics = Column(JSON)
    suggested_action = Column(JSON)
    example_posts = Column(JSON)
    creator_samples = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    trend = relationship("TrendModel", backref="proof_tiles")
