from datetime import datetime
from typing import List, Set, Optional
from ugc_backend.core.models import TrendStatus, MarketRegion, Platform
from ugc_backend.core.cluster import Cluster
from ugc_backend.core.metrics import calculate_validation_confidence


class TrendSignal:
    def __init__(
        self,
        signal_id: str,
        cluster: Cluster,
        status: TrendStatus,
        first_detected: datetime,
        min_creators: int = 10,
        min_regions: int = 2,
    ):
        self.signal_id = signal_id
        self.cluster = cluster
        self.status = status
        self.first_detected = first_detected
        self.last_updated = datetime.now()
        self.min_creators = min_creators
        self.min_regions = min_regions
        self._validation_confidence: Optional[float] = None

    @property
    def creator_replication_count(self) -> int:
        return len(self.cluster.unique_creators)

    @property
    def post_count(self) -> int:
        return len(self.cluster.posts)

    @property
    def platforms(self) -> Set[Platform]:
        return set(Platform(p) for p in self.cluster.platforms)

    @property
    def regions(self) -> Set[MarketRegion]:
        return set(MarketRegion(r) for r in self.cluster.regions)

    @property
    def primary_hashtags(self) -> List[str]:
        return self.cluster.primary_hashtags

    @property
    def detection_confidence(self) -> float:
        return self.cluster.calculate_health().detection_confidence

    @property
    def validation_confidence(self) -> float:
        if self._validation_confidence is None:
            self._validation_confidence = calculate_validation_confidence(
                creator_count=self.creator_replication_count,
                region_count=len(self.regions),
                min_creators=self.min_creators,
                min_regions=self.min_regions,
            )
        return self._validation_confidence

    def update_status(self, new_status: TrendStatus):
        self.status = new_status
        self.last_updated = datetime.now()


class TrendValidator:
    def __init__(
        self,
        min_creators: int = 10,
        min_regions: int = 2,
        confidence_threshold: float = 0.7,
    ):
        self.min_creators = min_creators
        self.min_regions = min_regions
        self.confidence_threshold = confidence_threshold

    def validate_cluster(self, cluster: Cluster, first_detected: datetime) -> TrendSignal:
        """
        validation process:
        1. check cluster health (must be >0.5)
        2. count unique creators (need min_creators+)
        3. check cross-platform presence
        4. check cross-region spread
        5. calculate confidence scores
        6. determine trend status
        """
        health = cluster.calculate_health()
        
        if health.health_score < 0.5:
            status = TrendStatus.emerging
        else:
            creator_count = len(cluster.unique_creators)
            region_count = len(cluster.regions)
            platform_count = len(cluster.platforms)

            validation_conf = calculate_validation_confidence(
                creator_count=creator_count,
                region_count=region_count,
                min_creators=self.min_creators,
                min_regions=self.min_regions,
            )

            if validation_conf >= self.confidence_threshold:
                status = TrendStatus.validated
            elif creator_count >= self.min_creators and platform_count >= 2:
                status = TrendStatus.validating
            elif creator_count >= self.min_creators:
                status = TrendStatus.validating
            else:
                status = TrendStatus.emerging

        signal_id = f"signal_{cluster.cluster_id}"
        signal = TrendSignal(
            signal_id=signal_id,
            cluster=cluster,
            status=status,
            first_detected=first_detected,
            min_creators=self.min_creators,
            min_regions=self.min_regions,
        )

        return signal

    def revalidate_signal(self, signal: TrendSignal) -> TrendSignal:
        """
        revalidate existing signal with updated cluster data
        useful for tracking trend lifecycle
        """
        return self.validate_cluster(signal.cluster, signal.first_detected)
