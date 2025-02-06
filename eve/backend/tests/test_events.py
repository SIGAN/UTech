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
def sample_event_data():
    return {
        "title": "Test Event",
        "author_email": "test@example.com"
    }

@pytest.fixture
def full_event_data():
    return {
        "title": "Test Event",
        "description": "Test Description",
        "place": "Test Place",
        "start_time": (datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None),
        "end_time": (datetime.now(UTC) + timedelta(days=1, hours=2)).replace(tzinfo=None),
        "food": "Test Food",
        "drinks": "Test Drinks",
        "program": "Test Program",
        "parking_info": "Test Parking",
        "music": "Test Music",
        "theme": "Test Theme",
        "age_restrictions": "18+",
        "author_email": "test@example.com"
    }

def test_create_minimal_event(db_session, sample_event_data):
    event = event_use_cases.create_event(db_session, **sample_event_data)
    
    assert event.id is not None
    assert event.title == sample_event_data["title"]
    assert event.author_email == sample_event_data["author_email"]
    assert event.description is None
    assert event.place is None
    assert event.start_time is None
    assert event.end_time is None
    assert event.food is None
    assert event.drinks is None
    assert event.program is None
    assert event.parking_info is None
    assert event.music is None
    assert event.theme is None
    assert event.age_restrictions is None

def test_create_full_event(db_session, full_event_data):
    event = event_use_cases.create_event(db_session, **full_event_data)
    
    assert event.id is not None
    for key, value in full_event_data.items():
        if key in ['start_time', 'end_time']:
            assert getattr(event, key + '_utc') == value.replace(tzinfo=UTC)
        else:
            assert getattr(event, key) == value

def test_get_event(db_session, full_event_data):
    # Create event
    event = event_use_cases.create_event(db_session, **full_event_data)
    
    # Get event
    retrieved_event = event_use_cases.get_event(db_session, event.id)
    assert retrieved_event is not None
    assert retrieved_event.id == event.id
    
    # Try to get non-existent event
    non_existent = event_use_cases.get_event(db_session, 9999)
    assert non_existent is None

def test_get_events(db_session, full_event_data):
    # Create multiple events
    event1 = event_use_cases.create_event(db_session, **full_event_data)
    event2_data = full_event_data.copy()
    event2_data["title"] = "Test Event 2"
    event2 = event_use_cases.create_event(db_session, **event2_data)
    
    # Get all events
    events = event_use_cases.get_events(db_session)
    assert len(events) == 2
    assert any(e.id == event1.id for e in events)
    assert any(e.id == event2.id for e in events)

def test_update_event(db_session, full_event_data):
    # Create event
    event = event_use_cases.create_event(db_session, **full_event_data)
    
    # Update event as owner
    updated_data = {"title": "Updated Title", "description": "Updated Description"}
    updated_event = event_use_cases.update_event(
        db_session,
        event.id,
        full_event_data["author_email"],
        **updated_data
    )
    
    assert updated_event is not None
    assert updated_event.title == "Updated Title"
    assert updated_event.description == "Updated Description"
    
    # Try to update as non-owner
    with pytest.raises(ValueError, match=r".*not authorized.*"):
        event_use_cases.update_event(
            db_session,
            event.id,
            "wrong@example.com",
            **updated_data
        )

def test_update_optional_fields(db_session, sample_event_data):
    # Create minimal event
    event = event_use_cases.create_event(db_session, **sample_event_data)
    assert event.description is None
    assert event.place is None
    assert event.start_time is None
    assert event.end_time is None
    
    # Add optional fields
    update_data = {
        "description": "Added Description",
        "place": "Added Place",
        "start_time": (datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None),
        "end_time": (datetime.now(UTC) + timedelta(days=1, hours=2)).replace(tzinfo=None)
    }
    
    updated_event = event_use_cases.update_event(
        db_session,
        event.id,
        sample_event_data["author_email"],
        **update_data
    )
    
    assert updated_event.description == "Added Description"
    assert updated_event.place == "Added Place"
    assert updated_event.start_time_utc == update_data["start_time"].replace(tzinfo=UTC)
    assert updated_event.end_time_utc == update_data["end_time"].replace(tzinfo=UTC)
    
    # Remove optional fields
    remove_data = {
        "description": None,
        "place": None,
        "start_time": None,
        "end_time": None
    }
    
    updated_event = event_use_cases.update_event(
        db_session,
        event.id,
        sample_event_data["author_email"],
        **remove_data
    )
    
    assert updated_event.description is None
    assert updated_event.place is None
    assert updated_event.start_time is None
    assert updated_event.end_time is None

def test_multiple_events_per_author(db_session, full_event_data):
    """Test that a user can create multiple events."""
    # Create first event
    event1 = event_use_cases.create_event(db_session, **full_event_data)
    
    # Create second event with same author
    event2_data = full_event_data.copy()
    event2_data["title"] = "Second Event"
    event2 = event_use_cases.create_event(db_session, **event2_data)
    
    # Create third event with same author
    event3_data = full_event_data.copy()
    event3_data["title"] = "Third Event"
    event3 = event_use_cases.create_event(db_session, **event3_data)
    
    # Get user's events
    user_events = event_use_cases.get_user_events(db_session, full_event_data["author_email"])
    assert len(user_events) == 3
    assert any(e.id == event1.id and e.title == full_event_data["title"] for e in user_events)
    assert any(e.id == event2.id and e.title == "Second Event" for e in user_events)
    assert any(e.id == event3.id and e.title == "Third Event" for e in user_events)

def test_delete_event(db_session, full_event_data):
    # Create event
    event = event_use_cases.create_event(db_session, **full_event_data)
    
    # Try to delete as non-owner
    with pytest.raises(ValueError, match=r".*not authorized.*"):
        event_use_cases.delete_event(db_session, event.id, "wrong@example.com")
    assert event_use_cases.get_event(db_session, event.id) is not None
    
    # Delete as owner
    result = event_use_cases.delete_event(db_session, event.id, full_event_data["author_email"])
    assert result
    assert event_use_cases.get_event(db_session, event.id) is None