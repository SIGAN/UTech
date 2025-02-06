import pytest
from datetime import datetime, timedelta, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

@pytest.fixture
def test_comments(db_session, test_event):
    """Create test comments with different timestamps and users"""
    comments_data = [
        {
            "event_id": test_event.id,
            "user_id": "user1@example.com",
            "message": "First comment",
            "rating": 5,
            "author_email": "user1@example.com"
        },
        {
            "event_id": test_event.id,
            "user_id": "user2@example.com",
            "message": "Second comment",
            "rating": 4,
            "author_email": "user2@example.com"
        },
        {
            "event_id": test_event.id,
            "user_id": "user3@example.com",
            "message": "Third comment",
            "rating": 3,
            "author_email": "user3@example.com"
        }
    ]
    
    comments = []
    for data in comments_data:
        comment = comment_use_cases.create_comment(db_session, **data)
        comments.append(comment)
    return comments

def test_comment_on_nonexistent_event(db_session):
    """Test commenting on a non-existent event"""
    comment_data = {
        "event_id": 99999,  # Non-existent event ID
        "user_id": "user@example.com",
        "message": "Test comment",
        "rating": 5,
        "author_email": "user@example.com"
    }
    
    with pytest.raises(ValueError, match=r".*event not found.*"):
        comment_use_cases.create_comment(db_session, **comment_data)

def test_comment_ordering(db_session, test_event):
    """Test comment list ordering"""
    # Create comments with explicit timestamps
    for i in range(3):
        comment_use_cases.create_comment(
            db_session,
            event_id=test_event.id,
            user_id=f"user{i}@example.com",
            message=f"Comment {i}",
            rating=5,
            author_email=f"user{i}@example.com"
        )
    
    # Get comments
    comments = comment_use_cases.get_event_comments(db_session, test_event.id)
    
    # Verify chronological order
    for i in range(1, len(comments)):
        assert comments[i-1].id < comments[i].id

def test_comment_author_permissions(db_session, test_event):
    """Test comment author permissions"""
    # Create a comment
    comment = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id="user@example.com",
        message="Original message",
        rating=5,
        author_email="user@example.com"
    )
    
    # Try to update comment as different user
    with pytest.raises(ValueError, match=r".*not authorized.*"):
        comment_use_cases.update_comment(
            db_session,
            comment.id,
            "other@example.com",
            message="Modified message",
            rating=4
        )
    
    # Try to delete comment as different user
    with pytest.raises(ValueError, match=r".*not authorized.*"):
        comment_use_cases.delete_comment(
            db_session,
            comment.id,
            "other@example.com"
        )

def test_comment_event_cascade_delete(db_session, test_event, test_comments):
    """Test that comments are deleted when event is deleted"""
    # Get comment IDs before deletion
    comment_ids = [c.id for c in test_comments]
    
    # Delete event
    event_use_cases.delete_event(db_session, test_event.id, test_event.author_email)
    
    # Verify comments are deleted
    for comment_id in comment_ids:
        assert comment_use_cases.get_comment(db_session, comment_id) is None

def test_comment_rating_aggregation(db_session, test_event):
    """Test comment rating aggregation"""
    # Create comments with different ratings
    ratings = [5, 3, 4, 5, 2]
    for i, rating in enumerate(ratings):
        comment_use_cases.create_comment(
            db_session,
            event_id=test_event.id,
            user_id=f"user{i}@example.com",
            message=f"Comment {i}",
            rating=rating,
            author_email=f"user{i}@example.com"
        )
    
    # Get aggregated ratings
    stats = comment_use_cases.get_event_rating_stats(db_session, test_event.id)
    
    assert stats["average_rating"] == sum(ratings) / len(ratings)
    assert stats["total_ratings"] == len(ratings)
    assert stats["rating_distribution"] == {
        1: 0,
        2: 1,
        3: 1,
        4: 1,
        5: 2
    }

def test_comment_edit_history(db_session, test_event):
    """Test comment edit history tracking"""
    # Note: This test is a placeholder since we don't track edit history yet
    # Create a comment
    comment = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id="user@example.com",
        message="Original message",
        rating=3,
        author_email="user@example.com"
    )
    
    # Make multiple edits
    edits = [
        ("Updated message 1", 4),
        ("Updated message 2", 5),
        ("Final message", 4)
    ]
    
    for message, rating in edits:
        comment = comment_use_cases.update_comment(
            db_session,
            comment.id,
            "user@example.com",
            message=message,
            rating=rating
        )
    
    # Get current state (since we don't track history yet)
    history = comment_use_cases.get_comment_history(db_session, comment.id)
    assert len(history) == 1  # Only current state
    assert history[0]["message"] == "Final message"
    assert history[0]["rating"] == 4

def test_multiple_comments_per_user(db_session, test_event):
    """Test that multiple comments from the same user are allowed"""
    user_email = "user@example.com"
    
    # Create first comment
    comment1 = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id=user_email,
        message="First comment",
        rating=5,
        author_email=user_email
    )
    
    # Create second comment from same user
    comment2 = comment_use_cases.create_comment(
        db_session,
        event_id=test_event.id,
        user_id=user_email,
        message="Second comment",
        rating=4,
        author_email=user_email
    )
    
    # Verify both comments exist
    comments = comment_use_cases.get_event_comments(db_session, test_event.id)
    assert len(comments) == 2
    assert any(c.id == comment1.id and c.message == "First comment" for c in comments)
    assert any(c.id == comment2.id and c.message == "Second comment" for c in comments)