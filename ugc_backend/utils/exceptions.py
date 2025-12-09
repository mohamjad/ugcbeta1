class UGCBackendException(Exception):
    """base exception for ugc backend"""
    pass


class IngestionError(UGCBackendException):
    """error during data ingestion"""
    pass


class ClusteringError(UGCBackendException):
    """error during clustering"""
    pass


class ValidationError(UGCBackendException):
    """error during trend validation"""
    pass


class DatabaseError(UGCBackendException):
    """error during database operations"""
    pass
