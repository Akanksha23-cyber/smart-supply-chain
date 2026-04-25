"""Database initialization and migration setup."""
import os
import sys
from alembic.config import Config
from alembic import command
from app.db.database import engine, Base
from app.models.models import *  # noqa

def init_alembic():
    """Initialize Alembic for migrations."""
    alembic_cfg = Config("alembic.ini")
    command.init(alembic_cfg, "alembic")
    print("✅ Alembic initialized")


def create_all_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")


def drop_all_tables():
    """Drop all database tables (use with caution)."""
    print("⚠️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tables dropped")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "init":
            create_all_tables()
        elif command == "drop":
            confirm = input("⚠️  This will drop all tables. Confirm (yes/no): ")
            if confirm.lower() == "yes":
                drop_all_tables()
            else:
                print("Cancelled")
        elif command == "alembic":
            init_alembic()
        else:
            print("Usage: python db_init.py [init|drop|alembic]")
    else:
        print("Usage: python db_init.py [init|drop|alembic]")
