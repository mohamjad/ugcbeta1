from datetime import datetime, timedelta
from ugc_backend.core.models import ContentPost, CreatorProfile, Platform, ContentType, MarketRegion, CreatorTier
from ugc_backend.core.metrics import (
    calculate_engagement_rate,
    calculate_velocity_score,
    calculate_creator_diversity,
    calculate_cluster_health,
    calculate_detection_confidence,
    calculate_validation_confidence,
)


def test_engagement_rate():
    creator = CreatorProfile(
        creator_id="test_1",
        username="test_user",
        platform=Platform.tiktok,
        follower_count=10000,
        avg_engagement_rate=0.05,
        tier=CreatorTier.micro,
        region=MarketRegion.us,
    )
    
    post = ContentPost(
        post_id="post_1",
        creator=creator,
        platform=Platform.tiktok,
        content_type=ContentType.video,
        caption="test",
        timestamp=datetime.now(),
        views=1000,
        likes=50,
        comments=5,
        shares=10,
        saves=5,
        first_seen=datetime.now(),
        last_captured=datetime.now(),
    )
    
    rate = calculate_engagement_rate(post)
    assert rate == 0.065


def test_velocity_score():
    creator = CreatorProfile(
        creator_id="test_1",
        username="test_user",
        platform=Platform.tiktok,
        follower_count=10000,
        avg_engagement_rate=0.05,
        tier=CreatorTier.micro,
        region=MarketRegion.us,
    )
    
    post = ContentPost(
        post_id="post_1",
        creator=creator,
        platform=Platform.tiktok,
        content_type=ContentType.video,
        caption="test",
        timestamp=datetime.now() - timedelta(hours=2),
        views=1000,
        likes=50,
        comments=5,
        shares=10,
        saves=5,
        first_seen=datetime.now() - timedelta(hours=2),
        last_captured=datetime.now(),
    )
    
    velocity = calculate_velocity_score(post)
    assert velocity > 0


def test_creator_diversity():
    creator1 = CreatorProfile(
        creator_id="test_1",
        username="user1",
        platform=Platform.tiktok,
        follower_count=10000,
        avg_engagement_rate=0.05,
        tier=CreatorTier.micro,
        region=MarketRegion.us,
    )
    
    creator2 = CreatorProfile(
        creator_id="test_2",
        username="user2",
        platform=Platform.tiktok,
        follower_count=20000,
        avg_engagement_rate=0.05,
        tier=CreatorTier.micro,
        region=MarketRegion.us,
    )
    
    posts = [
        ContentPost(
            post_id=f"post_{i}",
            creator=creator1 if i % 2 == 0 else creator2,
            platform=Platform.tiktok,
            content_type=ContentType.video,
            caption="test",
            timestamp=datetime.now(),
            views=1000,
            likes=50,
            comments=5,
            shares=10,
            saves=5,
            first_seen=datetime.now(),
            last_captured=datetime.now(),
        )
        for i in range(10)
    ]
    
    diversity = calculate_creator_diversity(posts)
    assert diversity == 0.2


def test_cluster_health():
    creator1 = CreatorProfile(
        creator_id="test_1",
        username="user1",
        platform=Platform.tiktok,
        follower_count=10000,
        avg_engagement_rate=0.05,
        tier=CreatorTier.micro,
        region=MarketRegion.us,
    )
    
    creator2 = CreatorProfile(
        creator_id="test_2",
        username="user2",
        platform=Platform.tiktok,
        follower_count=20000,
        avg_engagement_rate=0.05,
        tier=CreatorTier.micro,
        region=MarketRegion.us,
    )
    
    posts = [
        ContentPost(
            post_id=f"post_{i}",
            creator=creator1 if i % 2 == 0 else creator2,
            platform=Platform.tiktok,
            content_type=ContentType.video,
            caption="test",
            timestamp=datetime.now(),
            views=1000,
            likes=50,
            comments=5,
            shares=10,
            saves=5,
            first_seen=datetime.now(),
            last_captured=datetime.now(),
        )
        for i in range(10)
    ]
    
    health = calculate_cluster_health(posts)
    assert 0.0 <= health <= 1.0
