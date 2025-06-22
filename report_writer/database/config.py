"""
Database configuration and connection management

This module handles PostgreSQL connections, session management, and database configuration
for the Interactive Analytics Report Writer.
"""

import os
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def _get_database_url(self) -> str:
        """Construct database URL from environment variables"""
        # Check for full DATABASE_URL first (for production)
        if database_url := os.getenv("DATABASE_URL"):
            return database_url
        
        # Construct from individual components (for development)
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "report_writer")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres")
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine with optimized settings"""
        engine = create_engine(
            self.database_url,
            # Connection pool settings for production scalability
            poolclass=QueuePool,
            pool_size=20,  # Maximum number of permanent connections to keep
            max_overflow=30,  # Maximum number of connections to create beyond pool_size
            pool_pre_ping=True,  # Validate connections before use
            pool_recycle=3600,  # Recycle connections after 1 hour
            
            # Echo SQL queries in development
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
        )
        
        # Add connection event listeners for monitoring
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set database-specific settings on connection"""
            # This would be used for SQLite, but PostgreSQL doesn't need it
            pass
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log when a connection is checked out from the pool"""
            logger.debug("Connection checked out from pool")
        
        return engine
    
    def create_tables(self):
        """Create all database tables"""
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
    
    def drop_tables(self):
        """Drop all database tables (for testing/reset)"""
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")
    
    def get_session(self) -> Generator[Session, None, None]:
        """Dependency for getting database session in FastAPI"""
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    @contextmanager
    def get_session_context(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error(f"Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.engine.connect() as connection:
                connection.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global database instance
db_config = DatabaseConfig()

# Convenience functions for FastAPI dependency injection
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions"""
    yield from db_config.get_session()

def get_db_session():
    """Get a database session for manual use"""
    return db_config.SessionLocal()

# Database initialization functions
def init_database():
    """Initialize database (create tables if they don't exist)"""
    try:
        db_config.test_connection()
        db_config.create_tables()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def reset_database():
    """Reset database (drop and recreate all tables)"""
    try:
        db_config.drop_tables()
        db_config.create_tables()
        logger.info("Database reset successfully")
        return True
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False


# Connection health check
def check_database_health() -> dict:
    """Check database health for monitoring"""
    try:
        with db_config.engine.connect() as connection:
            result = connection.execute("SELECT version()")
            version = result.fetchone()[0]
            
            # Check connection pool status
            pool = db_config.engine.pool
            pool_status = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "invalid": pool.invalid(),
                "overflow": pool.overflow(),
            }
            
            return {
                "status": "healthy",
                "version": version,
                "pool_status": pool_status,
                "url": db_config.database_url.split("@")[-1],  # Hide credentials
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "url": db_config.database_url.split("@")[-1],  # Hide credentials
        } 