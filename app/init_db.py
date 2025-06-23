"""
Database initialization script for Contact Reconciliation Service.

This script creates the database tables and can be run independently
to set up the database schema.
"""

from database import create_tables, engine
from models import Base

def init_database():
    """Initialize the database with all required tables."""
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")
    
    # Print all table names that were created
    print("Created tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    init_database()
