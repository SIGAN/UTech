from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

import os

DATABASE_URL = "sqlite:///./data/eve.db"  # Relative to working directory
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "detect_types": 3},  # PARSE_DECLTYPES | PARSE_COLNAMES
    json_serializer=lambda obj: obj.isoformat() if isinstance(obj, datetime) else str(obj)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Create parent directory if it doesn't exist
    import os
    # Keep the leading slash by splitting after ////
    parts = DATABASE_URL.split('////')
    if len(parts) == 2:
        db_path = parts[1]  # This will keep the leading slash
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, mode=0o777, exist_ok=True)
        
        # Create database file with proper permissions if it doesn't exist
        if not os.path.exists(db_path):
            with open(db_path, 'w') as f:
                pass
            os.chmod(db_path, 0o666)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()