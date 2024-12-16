from typing import Optional
from .postgres import PostgresManager
from ..utils import settings, logger

_postgres_manager: Optional[PostgresManager] = None

def get_postgres_manager() -> PostgresManager:
    """
    Get or create a PostgresManager instance using settings.
    
    Returns:
        PostgresManager: Initialized database manager instance
    
    Note:
        Uses singleton pattern to avoid multiple database connections
    """
    global _postgres_manager
    
    if _postgres_manager is None:
        logger.info("Initializing new PostgresManager instance")
        _postgres_manager = PostgresManager(
            db_user=settings.DB_USER,
            db_password=settings.DB_PASSWORD,
            db_host=settings.DB_HOST,
            db_port=str(settings.DB_PORT),  # Convert to string as required by PostgresManager
            db_name=settings.DB_NAME
        )
    
    return _postgres_manager

def close_db_connection() -> None:
    """
    Close the database connection if it exists.
    Should be called when shutting down the application.
    """
    global _postgres_manager
    
    if _postgres_manager is not None:
        logger.info("Closing database connection")
        _postgres_manager.close()
        _postgres_manager = None