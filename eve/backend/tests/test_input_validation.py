import pytest
import re
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
def valid_event_data():
    """Base event data with valid fields"""
    now = datetime.now(UTC)
    return {
        "title": "Test Event",
        "description": "Test Description",
        "place": "Test Place",
        "start_time": (now + timedelta(days=1)).replace(tzinfo=None),
        "end_time": (now + timedelta(days=1, hours=2)).replace(tzinfo=None),
        "author_email": "test@example.com"
    }

@pytest.fixture
def valid_comment_data():
    """Base comment data with valid fields"""
    return {
        "message": "Test comment",
        "rating": 5,
        "user_id": "user@example.com",
        "author_email": "user@example.com"
    }

def test_email_validation(db_session, valid_event_data):
    """Test email format validation"""
    test_cases = [
        ("", "invalid email format"),
        ("notanemail", "invalid email format"),
        ("@nodomain", "invalid email format"),
        ("no@domain@com", "invalid email format"),
        ("spaces in@email.com", "invalid email format"),
        ("a" * 256 + "@example.com", "invalid email format"),
        ("test@" + "a" * 256 + ".com", "invalid email format"),
        ("test@.com", "invalid email format"),
        ("test@com.", "invalid email format"),
        ("test@-domain.com", "invalid email format"),
        ("test@domain-.com", "invalid email format"),
        ("<script>@hack.com", "invalid email format"),
    ]

    for email, expected_error in test_cases:
        # Test author email
        data = valid_event_data.copy()
        data["author_email"] = email
        with pytest.raises(ValueError, match=re.escape(expected_error)):
            event_use_cases.create_event(db_session, **data)

def test_text_field_validation(db_session, valid_event_data):
    """Test text field validation"""
    # Test empty required field
    data = valid_event_data.copy()
    data["title"] = ""
    with pytest.raises(ValueError, match=r".*cannot be empty.*"):
            event_use_cases.create_event(db_session, **data)

    # Test field length limits
    long_text = "a" * 1001  # Assuming 1000 char limit
    text_fields = ["title", "description", "place", "food", "drinks", 
                  "program", "parking_info", "music", "theme", "age_restrictions"]
    
    for field in text_fields:
        data = valid_event_data.copy()
        data[field] = long_text
        with pytest.raises(ValueError, match=r".*too long.*"):
            event_use_cases.create_event(db_session, **data)

    # Test HTML/script injection
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "<a href='javascript:alert('xss')'>click me</a>",
        "<!--[if gte IE 4]><script>alert('xss');</script><![endif]-->"
    ]

    for input_text in malicious_inputs:
        data = valid_event_data.copy()
        data["description"] = input_text
        with pytest.raises(ValueError, match=r".*contains invalid characters.*"):
            event_use_cases.create_event(db_session, **data)

def test_unicode_handling(db_session, valid_event_data):
    """Test handling of Unicode text"""
    unicode_texts = [
        "Café", # Latin-1
        "スタバ", # Japanese
        "кофе", # Cyrillic
        "☕", # Emoji
        "🎉 Party!", # Emoji with text
        "über", # German
        "café του", # Mixed scripts
    ]

    for text in unicode_texts:
        data = valid_event_data.copy()
        data["title"] = text
        event = event_use_cases.create_event(db_session, **data)
        assert event.title == text

def test_comment_validation(db_session, valid_event_data, valid_comment_data):
    """Test comment-specific validation"""
    # Create an event first
    event = event_use_cases.create_event(db_session, **valid_event_data)
    
    # Test invalid ratings
    invalid_ratings = [-1, 6, 2.5, "5", None]
    for rating in invalid_ratings:
        data = valid_comment_data.copy()
        data["rating"] = rating
        with pytest.raises(ValueError, match=r".*rating must be.*"):
            comment_use_cases.create_comment(db_session, event.id, **data)

    # Test empty message
    data = valid_comment_data.copy()
    data["message"] = ""
    with pytest.raises(ValueError, match=r".*message cannot be empty.*"):
        comment_use_cases.create_comment(db_session, event.id, **data)

    # Test message length
    data = valid_comment_data.copy()
    data["message"] = "a" * 1001  # Assuming 1000 char limit
    with pytest.raises(ValueError, match=r".*message too long.*"):
        comment_use_cases.create_comment(db_session, event.id, **data)

def test_whitespace_handling(db_session, valid_event_data):
    """Test handling of whitespace in text fields"""
    whitespace_cases = [
        "  Leading spaces",
        "Trailing spaces  ",
        "  Both ends  ",
        "Multiple    spaces",
        "Tabs\tand\tnewlines\n",
        "\n\nMultiple\n\nNewlines\n\n"
    ]

    for text in whitespace_cases:
        data = valid_event_data.copy()
        data["title"] = text
        event = event_use_cases.create_event(db_session, **data)
        # Verify whitespace is normalized (single spaces, no leading/trailing)
        normalized = re.sub(r'\s+', ' ', text.strip())
        assert event.title == normalized

def test_required_fields(db_session, valid_event_data):
    """Test required vs optional fields"""
    # Test required fields
    required_fields = ["title", "author_email"]
    
    for field in required_fields:
        data = valid_event_data.copy()
        data.pop(field)
        with pytest.raises((ValueError, TypeError), match=r".*required.*"):
            event_use_cases.create_event(db_session, **data)

    # Test optional fields can be None
    optional_fields = ["food", "drinks", "program", "parking_info", 
                      "music", "theme", "age_restrictions"]
    
    for field in optional_fields:
        data = valid_event_data.copy()
        data[field] = None
        event = event_use_cases.create_event(db_session, **data)
        assert getattr(event, field) is None