from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


# Use environment variable for database URI, fallback to provided PostgreSQL URI
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:YOUR-PASSWORD@db.mqvskwcyktgjdecucmxl.supabase.co:5432/postgres'
)
print(DATABASE_URL)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
