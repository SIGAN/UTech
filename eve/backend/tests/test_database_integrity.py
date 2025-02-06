import pytest
from datetime import datetime, timedelta, UTC
from sqlalchemy import create_engine, event as sqlalchemy_event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database import Base
from models import Event, EventComment
from use_cases import event_use_cases, comment_use_cases

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

@pytest.fixture
def test_event(db_session):
    """Create a test event"""
    event_data = {
        "title": "Test Event",
        "description": "Test Description",
        "place": "Test Place",
        "start_time": (datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None),
        "end_time": (datetime.now(UTC) + timedelta(days=1, hours=2)).replace(tzinfo=None),
        "author_email": "event@example.com"
    }
    return event_use_cases.create_event(db_session, **event_data)

def test_database_constraints(db_session):
    """Test database constraint enforcement"""
    # Test NOT NULL constraints
    event_data = {
        "title": None,  # Should be NOT NULL
        "description": "Test Description",
        "place": "Test Place",
        "start_time": (datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None),
        "end_time": (datetime.now(UTC) + timedelta(days=1, hours=2)).replace(tzinfo=None),
        "author_email": "test@example.com"
    }
    
    with pytest.raises((IntegrityError, ValueError)):
        event_use_cases.create_event(db_session, **event_data)
    
    # Test foreign key constraints
    comment_data = {
        "event_id": 99999,  # Non-existent event
        "user_id": "user@example.com",
        "message": "Test comment",
        "rating": 5,
        "author_email": "user@example.com"
    }
    
    with pytest.raises(ValueError):
        comment_use_cases.create_comment(db_session, **comment_data)

def test_cascade_deletes(db_session, test_event):
    """Test cascade delete behavior"""
    # Create comments
    comments = []
    for i in range(3):
        comment = comment_use_cases.create_comment(
            db_session,
            event_id=test_event.id,
            user_id=f"user{i}@example.com",
            message=f"Comment {i}",
            rating=5,
            author_email=f"user{i}@example.com"
        )
        comments.append(comment)
    
    # Store comment IDs
    comment_ids = [c.id for c in comments]
    
    # Delete event
    event_use_cases.delete_event(db_session, test_event.id, test_event.author_email)
    
    # Verify comments are deleted
    for comment_id in comment_ids:
        assert comment_use_cases.get_comment(db_session, comment_id) is None

def test_transaction_rollback(db_session):
    """Test transaction rollback on error"""
    # Create initial event
    event = event_use_cases.create_event(
        db_session,
        title="Test Event",
        description="Test Description",
        place="Test Place",
        start_time=(datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None),
        end_time=(datetime.now(UTC) + timedelta(days=1, hours=2)).replace(tzinfo=None),
        author_email="test@example.com"
    )
    
    # Try to update with invalid data
    try:
        event_use_cases.update_event(
            db_session,
            event.id,
            "test@example.com",
            title=None  # This should fail
        )
    except (IntegrityError, ValueError):
        db_session.rollback()
    
    # Verify event is unchanged
    event = event_use_cases.get_event(db_session, event.id)
    assert event.title == "Test Event"

def test_data_consistency(db_session):
    """Test data consistency across operations"""
    # Create event with comments
    event = event_use_cases.create_event(
        db_session,
        title="Test Event",
        description="Test Description",
        place="Test Place",
        start_time=(datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None),
        end_time=(datetime.now(UTC) + timedelta(days=1, hours=2)).replace(tzinfo=None),
        author_email="test@example.com"
    )
    
    # Add comments
    for i in range(3):
        comment_use_cases.create_comment(
            db_session,
            event_id=event.id,
            user_id=f"user{i}@example.com",
            message=f"Comment {i}",
            rating=5,
            author_email=f"user{i}@example.com"
        )
    
    # Update event
    event = event_use_cases.update_event(
        db_session,
        event.id,
        "test@example.com",
        title="Updated Event"
    )
    
    # Verify consistency
    assert event.title == "Updated Event"
    comments = comment_use_cases.get_event_comments(db_session, event.id)
    assert len(comments) == 3
    assert all(c.event_id == event.id for c in comments)

def test_database_connection_handling(db_session):
    """Test database connection handling"""
    # Test connection is active by executing a simple query
    result = db_session.execute(text("SELECT 1")).scalar()
    
    # Test connection after multiple operations
    for i in range(5):
        event = event_use_cases.create_event(
            db_session,
            title=f"Event {i}",
            description="Test Description",
            place="Test Place",
            start_time=(datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None),
            end_time=(datetime.now(UTC) + timedelta(days=1, hours=2)).replace(tzinfo=None),
            author_email="test@example.com"
        )
        assert event.id is not None
    
    # Verify connection is still good by executing a query
    result = db_session.execute(text("SELECT 1")).scalar()
    
    # Test connection after error
    try:
        event_use_cases.create_event(
            db_session,
            title=None,  # This should fail
            description="Test Description",
            place="Test Place",
            start_time=(datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None),
            end_time=(datetime.now(UTC) + timedelta(days=1, hours=2)).replace(tzinfo=None),
            author_email="test@example.com"
        )
    except (IntegrityError, ValueError):
        db_session.rollback()
    
    # Verify connection is still usable by executing a query
    result = db_session.execute(text("SELECT 1")).scalar()
    event = event_use_cases.create_event(
        db_session,
        title="Test Event",
        description="Test Description",
        place="Test Place",
        start_time=(datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None),
        end_time=(datetime.now(UTC) + timedelta(days=1, hours=2)).replace(tzinfo=None),
        author_email="test@example.com"
    )
    assert event.id is not None