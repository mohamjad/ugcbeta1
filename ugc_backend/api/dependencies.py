from typing import Generator
from sqlalchemy.orm import Session
from ugc_backend.db.session import Database
from ugc_backend.db.repository import (
    PostRepository,
    ClusterRepository,
    TrendRepository,
    ProofTileRepository,
)


_db_instance: Database = None


def init_db(database_url: str):
    global _db_instance
    _db_instance = Database(database_url)
    _db_instance.init_db()


def get_db():
    if _db_instance is None:
        raise RuntimeError("database not initialized. call init_db() first")
    session = _db_instance.SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_post_repository(session: Session = None) -> PostRepository:
    if session is None:
        session = next(get_db())
    return PostRepository(session)


def get_cluster_repository(session: Session = None) -> ClusterRepository:
    if session is None:
        session = next(get_db())
    return ClusterRepository(session)


def get_trend_repository(session: Session = None) -> TrendRepository:
    if session is None:
        session = next(get_db())
    return TrendRepository(session)


def get_proof_tile_repository(session: Session = None) -> ProofTileRepository:
    if session is None:
        session = next(get_db())
    return ProofTileRepository(session)
