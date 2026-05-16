from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load the environment variables from your .env file
load_dotenv()

# Get the URL directly from the environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Use the variable we just defined, not 'settings'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()