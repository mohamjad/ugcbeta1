from typing import List, Dict, Set, Optional
from collections import defaultdict
from dataclasses import dataclass
from ugc_backend.core.models import ContentPost
from ugc_backend.core.metrics import (
    calculate_cluster_health,
    calculate_creator_diversity,
    calculate_detection_confidence,
)
from ugc_backend.utils.exceptions import ClusteringError


@dataclass
class ClusterHealth:
    health_score: float
    creator_diversity: float
    engagement_strength: float
    velocity_score: float
    detection_confidence: float
    post_count: int
    creator_count: int


class Cluster:
    def __init__(self, cluster_id: str, posts: List[ContentPost], primary_hashtags: List[str]):
        self.cluster_id = cluster_id
        self.posts = posts
        self.primary_hashtags = primary_hashtags
        self._health: Optional[ClusterHealth] = None

    @property
    def unique_creators(self) -> Set[str]:
        return set(post.creator.creator_id for post in self.posts)

    @property
    def platforms(self) -> Set[str]:
        return set(post.platform.value for post in self.posts)

    @property
    def regions(self) -> Set[str]:
        return set(post.creator.region.value for post in self.posts)

    def calculate_health(
        self,
        creator_diversity_weight: float = 0.4,
        engagement_strength_weight: float = 0.3,
        velocity_weight: float = 0.3,
    ) -> ClusterHealth:
        if self._health is None:
            from ugc_backend.core.metrics import (
                calculate_engagement_strength,
                calculate_velocity_score,
                normalize_velocity,
            )

            diversity = calculate_creator_diversity(self.posts)
            engagement = calculate_engagement_strength(self.posts)
            
            velocities = [calculate_velocity_score(post) for post in self.posts]
            avg_velocity = sum(velocities) / len(velocities) if velocities else 0.0
            velocity_norm = normalize_velocity(avg_velocity)

            health_score = calculate_cluster_health(
                self.posts,
                creator_diversity_weight,
                engagement_strength_weight,
                velocity_weight,
            )

            detection_conf = calculate_detection_confidence(health_score, diversity)

            self._health = ClusterHealth(
                health_score=health_score,
                creator_diversity=diversity,
                engagement_strength=engagement,
                velocity_score=avg_velocity,
                detection_confidence=detection_conf,
                post_count=len(self.posts),
                creator_count=len(self.unique_creators),
            )

        return self._health


class ClusteringEngine:
    def __init__(
        self,
        min_shared_hashtags: int = 2,
        min_posts_per_cluster: int = 3,
        hashtag_similarity: float = 0.5,
        creator_diversity_weight: float = 0.4,
        engagement_strength_weight: float = 0.3,
        velocity_weight: float = 0.3,
    ):
        self.min_shared_hashtags = min_shared_hashtags
        self.min_posts_per_cluster = min_posts_per_cluster
        self.hashtag_similarity = hashtag_similarity
        self.creator_diversity_weight = creator_diversity_weight
        self.engagement_strength_weight = engagement_strength_weight
        self.velocity_weight = velocity_weight

    def cluster_posts(self, posts: List[ContentPost]) -> List[Cluster]:
        """
        rule-based hashtag clustering algorithm (fully transparent):
        1. build hashtag index (which posts have which tags)
        2. find hashtags appearing frequently together
        3. group posts sharing significant hashtags
        4. calculate cluster health metrics
        """
        if not posts:
            return []
        
        try:
            hashtag_index = self._build_hashtag_index(posts)
            cooccurrence = self._calculate_hashtag_cooccurrence(hashtag_index)
            clusters = self._group_posts_by_hashtags(
                posts,
                hashtag_index,
                cooccurrence,
            )

            cluster_objects = []
            for idx, (hashtags, cluster_posts) in enumerate(clusters.items()):
                if len(cluster_posts) < self.min_posts_per_cluster:
                    continue

                cluster = Cluster(
                    cluster_id=f"cluster_{idx:08x}",
                    posts=cluster_posts,
                    primary_hashtags=sorted(hashtags),
                )
                cluster.calculate_health(
                    self.creator_diversity_weight,
                    self.engagement_strength_weight,
                    self.velocity_weight,
                )
                cluster_objects.append(cluster)

            return cluster_objects
        except Exception as e:
            raise ClusteringError(f"failed to cluster posts: {str(e)}") from e

    def _build_hashtag_index(self, posts: List[ContentPost]) -> Dict[str, List[ContentPost]]:
        index = defaultdict(list)
        for post in posts:
            for hashtag in post.hashtags:
                index[hashtag].append(post)
        return dict(index)

    def _calculate_hashtag_cooccurrence(
        self,
        hashtag_index: Dict[str, List[ContentPost]],
    ) -> Dict[tuple, int]:
        cooccurrence = defaultdict(int)
        hashtags = list(hashtag_index.keys())

        for i, tag1 in enumerate(hashtags):
            for tag2 in hashtags[i + 1:]:
                posts1 = set(post.post_id for post in hashtag_index[tag1])
                posts2 = set(post.post_id for post in hashtag_index[tag2])
                shared = len(posts1 & posts2)
                if shared >= self.min_shared_hashtags:
                    cooccurrence[(tag1, tag2)] = shared

        return dict(cooccurrence)

    def _group_posts_by_hashtags(
        self,
        posts: List[ContentPost],
        hashtag_index: Dict[str, List[ContentPost]],
        cooccurrence: Dict[tuple, int],
    ) -> Dict[frozenset, List[ContentPost]]:
        clusters: Dict[frozenset, Set[ContentPost]] = defaultdict(set)

        for (tag1, tag2), count in cooccurrence.items():
            if count >= self.min_shared_hashtags:
                cluster_key = frozenset([tag1, tag2])
                posts1 = set(hashtag_index[tag1])
                posts2 = set(hashtag_index[tag2])
                clusters[cluster_key].update(posts1 & posts2)

        for post in posts:
            if len(post.hashtags) >= self.min_shared_hashtags:
                post_tags = frozenset(post.hashtags)
                if post_tags not in clusters:
                    clusters[post_tags] = set()
                clusters[post_tags].add(post)

        merged_clusters = self._merge_overlapping_clusters(clusters)

        return {tags: list(posts) for tags, posts in merged_clusters.items()}

    def _merge_overlapping_clusters(
        self,
        clusters: Dict[frozenset, Set[ContentPost]],
    ) -> Dict[frozenset, Set[ContentPost]]:
        merged = {}
        cluster_list = list(clusters.items())

        for tags, posts in cluster_list:
            merged_into = None
            for existing_tags, existing_posts in merged.items():
                overlap = len(tags & existing_tags)
                total_unique = len(tags | existing_tags)
                if total_unique > 0:
                    similarity = overlap / total_unique
                    if similarity >= self.hashtag_similarity:
                        merged_into = existing_tags
                        break

            if merged_into:
                merged[merged_into].update(posts)
            else:
                merged[tags] = posts

        return merged
