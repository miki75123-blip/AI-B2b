"""
Initialize script - Create database and test data
"""
import sys
import os

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, Base, SessionLocal
from app.models import *  # noqa


def init_database():
    """Initialize database"""
    print("[*] Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("[+] Database tables created")
    
    # Create test user
    from app.models.user import User
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == "admin@example.com").first()
        
        if not existing_user:
            test_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                company_name="Test Company",
                is_active=True,
                is_superuser=True
            )
            db.add(test_user)
            db.commit()
            print("[+] Test user created")
            print("    Email: admin@example.com")
            print("    Password: admin123")
        else:
            print("[o] Test user already exists")
            
    finally:
        db.close()
    
    print("\n[*] Database initialization complete!")


if __name__ == "__main__":
    init_database()
