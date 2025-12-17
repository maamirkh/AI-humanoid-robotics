"""
Database initialization script
Creates the required tables for the RAG Chatbot Backend
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import get_db_connection
from src.database_schema import SCHEMA_SQL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize the database with required tables"""
    conn = None
    try:
        # Get database connection
        conn_gen = get_db_connection()
        conn = next(conn_gen)

        # Execute schema SQL
        with conn.cursor() as cursor:
            cursor.execute(SCHEMA_SQL)

        conn.commit()
        logger.info("Database schema created successfully")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Initializing database schema...")
    initialize_database()
    logger.info("Database initialization completed successfully!")