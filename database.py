# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Get database URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# Log the connection attempt (hide password in logs)
if DATABASE_URL:
    # Mask password for logging
    masked_url = DATABASE_URL.replace(
        DATABASE_URL.split('@')[0].split(':')[-1] if '@' in DATABASE_URL else '',
        '****'
    )
    print(f"Connecting to: {masked_url}")

# Create database engine with connection pooling settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    connect_args={
        "connect_timeout": 10,  # 10 second timeout
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()