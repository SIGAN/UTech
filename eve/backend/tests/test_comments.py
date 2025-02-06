import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Event, EventComment
from use_cases import comment_use_cases, event_use_cases

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
    from datetime import datetime, timedelta, UTC
    event_data = {
        "title": "Test Event",
        "description": "Test Description",
        "place": "Test Place",
        "start_time": (datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None),
        "end_time": (datetime.now(UTC) + timedelta(days=1, hours=2)).replace(tzinfo=None),
        "author_email": "event@example.com"
    }
    return event_use_cases.create_event(db_session, **event_data)

def test_create_comment(db_session, test_event):
    comment = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id="user@example.com",
        message="Test Comment",
        rating=5,
        author_email="user@example.com"
    )
    
    assert comment.id is not None
    assert comment.event_id == test_event.id
    assert comment.user_id == "user@example.com"
    assert comment.message == "Test Comment"
    assert comment.rating == 5
    assert comment.author_email == "user@example.com"

def test_get_event_comments(db_session, test_event):
    # Create multiple comments
    comment1 = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id="user1@example.com",
        message="Comment 1",
        rating=4,
        author_email="user1@example.com"
    )
    
    comment2 = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id="user2@example.com",
        message="Comment 2",
        rating=5,
        author_email="user2@example.com"
    )
    
    comments = comment_use_cases.get_event_comments(db_session, test_event.id)
    assert len(comments) == 2
    assert any(c.id == comment1.id for c in comments)
    assert any(c.id == comment2.id for c in comments)

def test_update_comment(db_session, test_event):
    # Create comment
    comment = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id="user@example.com",
        message="Original Comment",
        rating=3,
        author_email="user@example.com"
    )
    
    # Update as owner
    updated_comment = comment_use_cases.update_comment(
        db_session,
        comment.id,
        "user@example.com",
        message="Updated Comment",
        rating=4
    )
    
    assert updated_comment is not None
    assert updated_comment.message == "Updated Comment"
    assert updated_comment.rating == 4
    
    # Try to update as non-owner
    with pytest.raises(ValueError, match=r".*not authorized.*"):
        comment_use_cases.update_comment(
            db_session,
            comment.id,
            "wrong@example.com",
            message="Wrong Update",
            rating=1
        )

def test_multiple_comments_from_same_user(db_session, test_event):
    """Test that a user can post multiple comments on the same event."""
    user_email = "user@example.com"
    
    # Create first comment
    comment1 = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id=user_email,
        message="First Comment",
        rating=4,
        author_email=user_email
    )
    
    # Create second comment from same user
    comment2 = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id=user_email,
        message="Second Comment",
        rating=5,
        author_email=user_email
    )
    
    # Verify both comments exist
    comments = comment_use_cases.get_event_comments(db_session, test_event.id)
    assert len(comments) == 2
    assert any(c.id == comment1.id and c.message == "First Comment" for c in comments)
    assert any(c.id == comment2.id and c.message == "Second Comment" for c in comments)

def test_delete_comment(db_session, test_event):
    # Create comment
    comment = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id="user@example.com",
        message="Test Comment",
        rating=5,
        author_email="user@example.com"
    )
    
    # Try to delete as non-owner
    with pytest.raises(ValueError, match=r".*not authorized.*"):
        comment_use_cases.delete_comment(db_session, comment.id, "wrong@example.com")
    assert comment_use_cases.get_comment(db_session, comment.id) is not None
    
    # Delete as owner
    result = comment_use_cases.delete_comment(db_session, comment.id, "user@example.com")
    assert result
    assert comment_use_cases.get_comment(db_session, comment.id) is None