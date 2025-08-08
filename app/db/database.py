from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys
from urllib.parse import quote_plus, unquote_plus

# Enable SQLAlchemy logging for debugging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Default database URL (should be overridden by environment variable in production)
DEFAULT_DB_URL = 'postgresql://postgres:password@db.mqvskwcyktgjdecucmxl.supabase.co:5432/postgres'

print("Using database URL from:", "environment variable" if os.getenv('DATABASE_URL') else "default")

# Get database URL from environment variable or use default
raw_db_url = os.getenv('DATABASE_URL', DEFAULT_DB_URL)

# Print the host for debugging (without credentials)
if '@' in raw_db_url:
    print(f"Connecting to database at: {raw_db_url.split('@')[-1]}")

# URL-encode the password if it contains special characters
if '@' in raw_db_url:
    try:
        # Split the URL into parts
        protocol_part, rest = raw_db_url.split('://', 1)
        auth_part, host_part = rest.split('@', 1)
        
        # Split auth part into username and password
        if ':' in auth_part:
            username, password = auth_part.split(':', 1)
            # URL-encode the password
            encoded_password = quote_plus(password)
            # Reconstruct the URL with encoded password
            DATABASE_URL = f"{protocol_part}://{username}:{encoded_password}@{host_part}"
        else:
            DATABASE_URL = raw_db_url
    except Exception as e:
        print(f"Error processing database URL: {e}")
        DATABASE_URL = raw_db_url  # Fall back to raw URL
else:
    DATABASE_URL = raw_db_url

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()
