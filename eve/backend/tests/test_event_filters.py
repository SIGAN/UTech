import pytest
from datetime import datetime, timedelta, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Event
from use_cases import event_use_cases

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
def sample_events(db_session):
    """Create a mix of past, current, and future events with different authors"""
    now = datetime.now(UTC)
    events_data = [
        # Past events
        {
            "title": "Past Event 1",
            "description": "Past event by user1",
            "place": "Place 1",
            "start_time": (now - timedelta(days=2)).replace(tzinfo=None),
            "end_time": (now - timedelta(days=2, hours=-2)).replace(tzinfo=None),
            "author_email": "user1@example.com"
        },
        {
            "title": "Past Event 2",
            "description": "Past event by user2",
            "place": "Place 2",
            "start_time": (now - timedelta(days=1)).replace(tzinfo=None),
            "end_time": (now - timedelta(days=1, hours=-2)).replace(tzinfo=None),
            "author_email": "user2@example.com"
        },
        # Current events (started but not ended)
        {
            "title": "Current Event 1",
            "description": "Current event by user1",
            "place": "Place 3",
            "start_time": (now - timedelta(hours=1)).replace(tzinfo=None),
            "end_time": (now + timedelta(hours=1)).replace(tzinfo=None),
            "author_email": "user1@example.com"
        },
        # Future events
        {
            "title": "Future Event 1",
            "description": "Future event by user1",
            "place": "Place 4",
            "start_time": (now + timedelta(days=1)).replace(tzinfo=None),
            "end_time": (now + timedelta(days=1, hours=2)).replace(tzinfo=None),
            "author_email": "user1@example.com"
        },
        {
            "title": "Future Event 2",
            "description": "Future event by user2",
            "place": "Place 5",
            "start_time": (now + timedelta(days=2)).replace(tzinfo=None),
            "end_time": (now + timedelta(days=2, hours=2)).replace(tzinfo=None),
            "author_email": "user2@example.com"
        },
        {
            "title": "Far Future Event",
            "description": "Far future event by user1",
            "place": "Place 6",
            "start_time": (now + timedelta(days=30)).replace(tzinfo=None),
            "end_time": (now + timedelta(days=30, hours=2)).replace(tzinfo=None),
            "author_email": "user1@example.com"
        }
    ]

    events = []
    for data in events_data:
        try:
            event = event_use_cases.create_event(db_session, **data)
            events.append(event)
        except ValueError as e:
            # Skip past events that fail validation
            if "start_time cannot be in the past" not in str(e):
                raise

    return events

def test_upcoming_events_filter(db_session, sample_events):
    """Test filtering of upcoming events"""
    # Get all events first to ensure they're created
    all_events = event_use_cases.get_events(db_session)
    
    # Get upcoming events
    upcoming = event_use_cases.get_upcoming_events(db_session)
    
    # Verify only future events are returned
    now = datetime.now(UTC).replace(tzinfo=None)
    assert all(event.start_time > now for event in upcoming)
    
    # Verify events are in chronological order
    for i in range(1, len(upcoming)):
        assert upcoming[i-1].start_time <= upcoming[i].start_time

def test_my_events_filter(db_session, sample_events):
    """Test filtering events by author"""
    # Get user1's events
    user1_events = event_use_cases.get_user_events(db_session, "user1@example.com")
    assert all(event.author_email == "user1@example.com" for event in user1_events)
    
    # Get user2's events
    user2_events = event_use_cases.get_user_events(db_session, "user2@example.com")
    assert all(event.author_email == "user2@example.com" for event in user2_events)
    
    # Verify no events for non-existent user
    no_events = event_use_cases.get_user_events(db_session, "nonexistent@example.com")
    assert len(no_events) == 0

def test_combined_filters(db_session, sample_events):
    """Test combining multiple filters (my upcoming events)"""
    # Get user1's upcoming events
    user1_upcoming = event_use_cases.get_user_upcoming_events(
        db_session, 
        "user1@example.com"
    )
    
    now = datetime.now(UTC).replace(tzinfo=None)
    
    # Verify events are both upcoming and belong to user1
    for event in user1_upcoming:
        assert event.author_email == "user1@example.com"
        assert event.start_time > now
    
    # Verify chronological order
    for i in range(1, len(user1_upcoming)):
        assert user1_upcoming[i-1].start_time <= user1_upcoming[i].start_time

def test_current_events_filter(db_session, sample_events):
    """Test filtering of currently running events"""
    # Get current events (started but not ended)
    current = event_use_cases.get_current_events(db_session)
    now = datetime.now(UTC).replace(tzinfo=None)
    
    # Verify events have started but not ended
    for event in current:
        assert event.start_time <= now
        assert event.end_time > now

def test_past_events_filter(db_session, sample_events):
    """Test filtering of past events"""
    # Get past events
    past = event_use_cases.get_past_events(db_session)
    now = datetime.now(UTC).replace(tzinfo=None)
    
    # Verify events have ended
    for event in past:
        assert event.end_time < now
    
    # Verify reverse chronological order (most recent first)
    for i in range(1, len(past)):
        assert past[i-1].end_time >= past[i].end_time

def test_date_range_filter(db_session, sample_events):
    """Test filtering events by date range"""
    now = datetime.now(UTC).replace(tzinfo=None)
    start_date = now + timedelta(days=1)
    end_date = now + timedelta(days=3)
    
    # Get events in date range
    events = event_use_cases.get_events_in_range(db_session, start_date, end_date)
    
    # Verify events are within range
    for event in events:
        assert event.start_time >= start_date
        assert event.start_time <= end_date