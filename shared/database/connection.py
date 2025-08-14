from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = os.getenv(
                "DATABASE_URL",
                "postgresql://coverage:coverage@postgres:5432/coverage_db"
            )

        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create all tables defined in models."""
        Base.metadata.create_all(bind=self.engine)

    def get_db(self):
        """Dependency to get database session."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Global database manager instance
db_manager = DatabaseManager()

# Convenience function for FastAPI dependency injection


def get_db():
    """FastAPI dependency for database sessions."""
    yield from db_manager.get_db()
