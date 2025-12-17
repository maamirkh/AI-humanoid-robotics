"""
Database connection utilities for Neon PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
import logging
from .config import Config

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection manager for Neon PostgreSQL"""

    def __init__(self):
        self.connection_string = Config.DATABASE_URL
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                self.connection_string,
                cursor_factory=RealDictCursor
            )
            logger.info("Successfully connected to Neon PostgreSQL database")
            return self.connection
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def get_connection(self):
        """Get database connection, reconnecting if necessary"""
        if not self.connection or self.connection.closed:
            self.connect()
        return self.connection

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# Global database instance
db = DatabaseConnection()

def get_db_connection():
    """Dependency to provide database connection"""
    conn = db.get_connection()
    try:
        yield conn
    finally:
        # Note: We don't close the connection here since we're using a connection pool
        # In a real application, you might want to implement proper connection pooling
        pass