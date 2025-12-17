"""
Script to reset the Qdrant collection with correct dimensions
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.vector_db import VectorDB

def reset_collection():
    """Reset the Qdrant collection with correct dimensions"""
    print("Resetting Qdrant collection with correct dimensions...")

    vector_db = VectorDB()

    # Delete existing collection
    try:
        vector_db.delete_collection()
        print("Deleted existing collection")
    except Exception as e:
        print(f"Could not delete collection (may not exist yet): {e}")

    # Create collection with correct dimensions (1024 for Cohere embeddings)
    vector_db.create_collection(vector_size=1024)
    print("Created new collection with 1024 dimensions")

    print("Collection reset completed successfully!")

if __name__ == "__main__":
    reset_collection()