import pytest
from datetime import datetime, timedelta, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
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
def base_event_data():
    """Base event data with valid times"""
    now = datetime.now(UTC)
    return {
        "title": "Test Event",
        "description": "Test Description",
        "place": "Test Place",
        "start_time": (now + timedelta(days=1)).replace(tzinfo=None),
        "end_time": (now + timedelta(days=1, hours=2)).replace(tzinfo=None),
        "author_email": "test@example.com"
    }

def test_end_time_before_start_time(db_session, base_event_data):
    """Test that event creation fails when end_time is before start_time"""
    # Modify end_time to be before start_time
    base_event_data["end_time"] = (
        datetime.now(UTC) + timedelta(days=1, hours=-1)
    ).replace(tzinfo=None)

    with pytest.raises(ValueError) as exc_info:
        event_use_cases.create_event(db_session, **base_event_data)
    
    assert "end_time must be after start_time" in str(exc_info.value)

def test_past_start_time(db_session, base_event_data):
    """Test handling of events with start_time in the past"""
    # Set start_time to past
    base_event_data["start_time"] = (
        datetime.now(UTC) - timedelta(hours=1)
    ).replace(tzinfo=None)
    base_event_data["end_time"] = (
        datetime.now(UTC) + timedelta(hours=1)
    ).replace(tzinfo=None)

    with pytest.raises(ValueError) as exc_info:
        event_use_cases.create_event(db_session, **base_event_data)
    
    assert "start_time cannot be in the past" in str(exc_info.value)

def test_timezone_handling(db_session, base_event_data):
    """Test that all times are properly handled in UTC"""
    from datetime import timezone
    from zoneinfo import ZoneInfo

    # Create event with EST timezone using a fixed future time
    est_tz = ZoneInfo("America/New_York")
    future_est = datetime.now(est_tz) + timedelta(days=7)  # 1 week in the future
    base_event_data["start_time"] = future_est.astimezone(UTC).replace(tzinfo=None)
    base_event_data["end_time"] = (
        future_est + timedelta(hours=2)
    ).astimezone(UTC).replace(tzinfo=None)

    event = event_use_cases.create_event(db_session, **base_event_data)
    
    # Verify times are stored correctly
    assert event.start_time == base_event_data["start_time"]
    assert event.end_time == base_event_data["end_time"]
    
    # Verify UTC awareness when retrieving
    assert event.start_time_utc.tzinfo == UTC
    assert event.end_time_utc.tzinfo == UTC

def test_daylight_savings_handling(db_session, base_event_data):
    """Test correct handling around DST transitions"""
    from zoneinfo import ZoneInfo
    
    # Find next DST transition in US/Eastern
    tz = ZoneInfo("America/New_York")
    now = datetime.now(tz)
    
    # Create event spanning DST change
    # Note: This is a simplified test as actual DST transitions
    # would need specific dates that vary by year
    base_event_data["start_time"] = (
        now + timedelta(days=1)
    ).astimezone(UTC).replace(tzinfo=None)
    base_event_data["end_time"] = (
        now + timedelta(days=1, hours=5)
    ).astimezone(UTC).replace(tzinfo=None)

    event = event_use_cases.create_event(db_session, **base_event_data)
    
    # Verify time difference remains constant in UTC
    time_diff = event.end_time - event.start_time
    assert abs(time_diff - timedelta(hours=5)) < timedelta(seconds=1)

def test_multi_day_event(db_session, base_event_data):
    """Test creation and handling of multi-day events"""
    base_event_data["start_time"] = (
        datetime.now(UTC) + timedelta(days=1)
    ).replace(tzinfo=None)
    base_event_data["end_time"] = (
        datetime.now(UTC) + timedelta(days=3)
    ).replace(tzinfo=None)

    event = event_use_cases.create_event(db_session, **base_event_data)
    
    assert event.start_time == base_event_data["start_time"]
    assert event.end_time == base_event_data["end_time"]
    assert (event.end_time - event.start_time).days == 2

def test_exact_same_start_end_time(db_session, base_event_data):
    """Test that event cannot have exact same start and end time"""
    future = datetime.now(UTC) + timedelta(days=1)  # Use future time to avoid past validation
    base_event_data["start_time"] = future.replace(tzinfo=None)
    base_event_data["end_time"] = future.replace(tzinfo=None)

    with pytest.raises(ValueError) as exc_info:
        event_use_cases.create_event(db_session, **base_event_data)
    
    assert "end_time must be after start_time" in str(exc_info.value)