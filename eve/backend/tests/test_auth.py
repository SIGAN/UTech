import pytest
from datetime import datetime, timedelta, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Session as DbSession
from use_cases import auth_use_cases

# Setup test database
TEST_DATABASE_URL = "sqlite:///data/test.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_session(db_session):
    email = "test@example.com"
    session_id = auth_use_cases.create_session(db_session, email)
    
    assert session_id is not None
    db_session_obj = db_session.query(DbSession).filter(DbSession.id == session_id).first()
    assert db_session_obj is not None
    assert db_session_obj.user_email == email
    assert db_session_obj.expires_at_utc > datetime.now(UTC)

def test_validate_session(db_session):
    # Create a valid session
    email = "test@example.com"
    session_id = auth_use_cases.create_session(db_session, email)
    
    # Test valid session
    is_valid, user_email = auth_use_cases.validate_session(db_session, session_id)
    assert is_valid
    assert user_email == email
    
    # Test invalid session
    is_valid, user_email = auth_use_cases.validate_session(db_session, "invalid-session")
    assert not is_valid
    assert user_email is None
    
    # Test expired session
    session = db_session.query(DbSession).filter(DbSession.id == session_id).first()
    session.expires_at = (datetime.now(UTC) - timedelta(hours=1)).replace(tzinfo=None)
    db_session.commit()
    
    is_valid, user_email = auth_use_cases.validate_session(db_session, session_id)
    assert not is_valid
    assert user_email is None

def test_logout(db_session):
    email = "test@example.com"
    session_id = auth_use_cases.create_session(db_session, email)
    
    # Verify session exists
    session = db_session.query(DbSession).filter(DbSession.id == session_id).first()
    assert session is not None
    
    # Logout
    auth_use_cases.logout(db_session, session_id)
    
    # Verify session is deleted
    session = db_session.query(DbSession).filter(DbSession.id == session_id).first()
    assert session is None