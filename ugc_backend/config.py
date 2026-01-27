import os
import yaml
from pathlib import Path
from typing import Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ugc_intelligence"
    redis_url: str = "redis://localhost:6379/0"
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_enabled: bool = True
    
    logging_level: str = "INFO"
    logging_file: str = "logs/backend.log"
    
    early_detection_hours: int = 48
    validation_hours: int = 168
    saturation_hours: int = 336
    
    min_shared_hashtags: int = 2
    min_posts_per_cluster: int = 3
    hashtag_similarity: float = 0.5
    
    min_creators: int = 10
    min_regions: int = 2
    confidence_threshold: float = 0.7
    
    creator_diversity_weight: float = 0.4
    engagement_strength_weight: float = 0.3
    velocity_weight: float = 0.3
    
    tiktok_api_key: str = ""
    tiktok_rate_limit: int = 100
    
    xiaohongshu_enabled: bool = True
    xiaohongshu_rate_limit: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    if Path(config_path).exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config or {}
    return {}


def get_settings() -> Settings:
    config = load_config()
    settings = Settings()
    
    if "database" in config:
        db_config = config["database"]
        settings.database_url = os.getenv(
            "DATABASE_URL",
            f"postgresql://{db_config.get('user', 'postgres')}:{db_config.get('password', 'postgres')}@{db_config.get('host', 'localhost')}:{db_config.get('port', 5432)}/{db_config.get('name', 'ugc_intelligence')}"
        )
    
    if "api" in config:
        api_config = config["api"]
        settings.api_host = api_config.get("host", "0.0.0.0")
        settings.api_port = api_config.get("port", 8000)
        settings.cors_enabled = api_config.get("cors_enabled", True)
    
    if "windows" in config:
        windows_config = config["windows"]
        settings.early_detection_hours = windows_config.get("early_detection", 48)
        settings.validation_hours = windows_config.get("validation", 168)
        settings.saturation_hours = windows_config.get("saturation", 336)
    
    if "clustering" in config:
        cluster_config = config["clustering"]
        settings.min_shared_hashtags = cluster_config.get("min_shared_hashtags", 2)
        settings.min_posts_per_cluster = cluster_config.get("min_posts_per_cluster", 3)
        settings.hashtag_similarity = cluster_config.get("hashtag_similarity", 0.5)
        settings.creator_diversity_weight = cluster_config.get("creator_diversity_weight", 0.4)
        settings.engagement_strength_weight = cluster_config.get("engagement_strength_weight", 0.3)
        settings.velocity_weight = cluster_config.get("velocity_weight", 0.3)
    
    if "validation" in config:
        validation_config = config["validation"]
        settings.min_creators = validation_config.get("min_creators", 10)
        settings.min_regions = validation_config.get("min_regions", 2)
        settings.confidence_threshold = validation_config.get("confidence_threshold", 0.7)
    
    if "platforms" in config:
        platforms_config = config["platforms"]
        if "tiktok" in platforms_config:
            tiktok_config = platforms_config["tiktok"]
            settings.tiktok_api_key = os.getenv("TIKTOK_API_KEY", tiktok_config.get("api_key", ""))
            settings.tiktok_rate_limit = tiktok_config.get("rate_limit", 100)
        
        if "xiaohongshu" in platforms_config:
            xhs_config = platforms_config["xiaohongshu"]
            settings.xiaohongshu_enabled = xhs_config.get("enabled", True)
            settings.xiaohongshu_rate_limit = xhs_config.get("rate_limit", 60)
    
    return settings
