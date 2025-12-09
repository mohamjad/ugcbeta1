from typing import List
from datetime import datetime
from ugc_backend.core.models import ContentPost, CreatorProfile


def calculate_engagement_rate(post: ContentPost) -> float:
    """
    formula: (likes + comments + shares) / views
    range: 0.0 to ∞ (though >1.0 is rare)
    interpretation: industry standard metric
    threshold: 0.05 (5%) is typically good
    """
    if post.views == 0:
        return 0.0
    return (post.likes + post.comments + post.shares) / post.views


def calculate_velocity_score(post: ContentPost) -> float:
    """
    formula: (current_engagement - initial_engagement) / hours_elapsed
    units: engagements per hour
    interpretation: rate of growth
    threshold: >100/hour indicates viral potential
    
    note: for initial implementation, we use total_engagement / hours_since_first_seen
    in production, track initial_engagement separately via recapture
    """
    hours = post.hours_since_first_seen
    if hours == 0:
        return 0.0
    return post.total_engagement / hours


def calculate_creator_diversity(posts: List[ContentPost]) -> float:
    """
    formula: unique_creators / total_posts
    range: 0.0 to 1.0
    interpretation:
      - 1.0 = every post is a different creator (ideal)
      - 0.1 = one creator dominates (weak signal)
    threshold: >0.5 for valid trend
    """
    if not posts:
        return 0.0
    unique_creators = len(set(post.creator.creator_id for post in posts))
    return unique_creators / len(posts)


def calculate_engagement_strength(posts: List[ContentPost]) -> float:
    """
    formula: average(engagement_rate) across all posts
    range: 0.0 to ∞
    interpretation: average engagement rate of cluster
    """
    if not posts:
        return 0.0
    rates = [calculate_engagement_rate(post) for post in posts]
    return sum(rates) / len(rates)


def normalize_velocity(velocity: float, max_velocity: float = 1000.0) -> float:
    """
    normalize velocity score to 0.0-1.0 range
    max_velocity is configurable threshold (default 1000 engagements/hour)
    """
    if max_velocity == 0:
        return 0.0
    return min(velocity / max_velocity, 1.0)


def calculate_cluster_health(
    posts: List[ContentPost],
    creator_diversity_weight: float = 0.4,
    engagement_strength_weight: float = 0.3,
    velocity_weight: float = 0.3,
) -> float:
    """
    formula:
      (creator_diversity × creator_diversity_weight) +
      (engagement_strength × engagement_strength_weight) +
      (velocity_normalized × velocity_weight)
    
    range: 0.0 to 1.0
    weights adjustable based on vertical
    threshold: >0.5 for consideration
    
    weights default to:
      - 40% creator diversity: multiple creators = stronger signal
      - 30% engagement: high engagement = audience resonance
      - 30% velocity: fast growth = trend potential
    """
    if not posts:
        return 0.0
    
    diversity = calculate_creator_diversity(posts)
    engagement = calculate_engagement_strength(posts)
    
    velocities = [calculate_velocity_score(post) for post in posts]
    avg_velocity = sum(velocities) / len(velocities) if velocities else 0.0
    velocity_norm = normalize_velocity(avg_velocity)
    
    health = (
        diversity * creator_diversity_weight +
        engagement * engagement_strength_weight +
        velocity_norm * velocity_weight
    )
    
    return min(health, 1.0)


def calculate_detection_confidence(
    cluster_health: float,
    creator_diversity: float,
) -> float:
    """
    formula: (cluster_health + creator_diversity) / 2
    range: 0.0 to 1.0
    interpretation: how confident we are this is a cluster
    used for: filtering noise
    """
    return (cluster_health + creator_diversity) / 2.0


def calculate_validation_confidence(
    creator_count: int,
    region_count: int,
    min_creators: int = 10,
    min_regions: int = 2,
) -> float:
    """
    formula:
      creator_factor = min(creator_count / min_creators, 1.0)
      region_factor = min(region_count / min_regions, 1.0)
      confidence = (creator_factor + region_factor) / 2
    
    range: 0.0 to 1.0
    interpretation: how confident this is a real trend
    threshold: >0.7 for validated status
    """
    creator_factor = min(creator_count / min_creators, 1.0) if min_creators > 0 else 0.0
    region_factor = min(region_count / min_regions, 1.0) if min_regions > 0 else 0.0
    return (creator_factor + region_factor) / 2.0


def calculate_saturation_level(
    posts: List[ContentPost],
    days_active: float,
) -> float:
    """
    formula: posts_per_day / days_active
    units: posts per day
    interpretation:
      - rising: trend growing
      - stable: trend sustained
      - falling: trend saturating
    threshold: <1.0 posts/day = saturated
    """
    if days_active == 0:
        return 0.0
    return len(posts) / days_active
