from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Event
import re

def validate_email(email: str) -> None:
    """Validate email format"""
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@(?!-)[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9](?<!-)\.[a-zA-Z]{2,}$'
    
    if not email or not isinstance(email, str) or len(email) > 255 or re.search(r"[<>'\"]", email) or not re.match(pattern, email):
        raise ValueError("invalid email format")

def normalize_text(value: str) -> str:
    """Normalize text by removing extra whitespace"""
    if not value:
        return value
    # Replace tabs and newlines with spaces
    value = re.sub(r'[\t\n\r]+', ' ', value)
    # Replace multiple spaces with single space and strip
    return re.sub(r'\s+', ' ', value).strip()

def validate_text_field(field_name: str, value: str, required: bool = True, max_length: int = 1000) -> str:
    """Validate and normalize text field"""
    if not value:
        value = ""
    
    # Normalize whitespace
    normalized = normalize_text(value)
    
    if required and not normalized:
        raise ValueError(f"{field_name} cannot be empty")
    if len(normalized) > max_length:
        raise ValueError(f"{field_name} is too long (max {max_length} characters)")
    if re.search(r"<[^>]*script|javascript:|onerror=|onclick=", normalized, re.I):
        raise ValueError(f"{field_name} contains invalid characters")
    
    return normalized

def validate_event_times(start_time: Optional[datetime], end_time: Optional[datetime]) -> None:
    """Validate event start and end times"""
    # If either time is None, skip validation
    if start_time is None or end_time is None:
        return

    now = datetime.now(UTC).replace(tzinfo=None)
    
    # Ensure times are naive UTC
    if start_time.tzinfo is not None or end_time.tzinfo is not None:
        raise ValueError("Times must be naive UTC datetimes")
    
    # Check end time is after start time
    if end_time <= start_time:
        raise ValueError("end_time must be after start_time")
    
    # Check start time is not in the past
    if start_time < now:
        raise ValueError("start_time cannot be in the past")

def create_event(
    db: Session,
    title: str,
    author_email: str,
    description: Optional[str] = None,
    place: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    food: Optional[str] = None,
    drinks: Optional[str] = None,
    program: Optional[str] = None,
    parking_info: Optional[str] = None,
    music: Optional[str] = None,
    theme: Optional[str] = None,
    age_restrictions: Optional[str] = None
) -> Event:
    # Validate required fields
    validate_email(author_email)
    title = validate_text_field("title", title)
    
    # Validate optional text fields
    if description is not None:
        description = validate_text_field("description", description, required=False)
    if place is not None:
        place = validate_text_field("place", place, required=False)
    if food is not None:
        food = validate_text_field("food", food, required=False)
    if drinks is not None:
        drinks = validate_text_field("drinks", drinks, required=False)
    if program is not None:
        program = validate_text_field("program", program, required=False)
    if parking_info is not None:
        parking_info = validate_text_field("parking_info", parking_info, required=False)
    if music is not None:
        music = validate_text_field("music", music, required=False)
    if theme is not None:
        theme = validate_text_field("theme", theme, required=False)
    if age_restrictions is not None:
        age_restrictions = validate_text_field("age_restrictions", age_restrictions, required=False)
    
    # Validate dates if provided
    if start_time is not None or end_time is not None:
        validate_event_times(start_time, end_time)
    event = Event(
        title=title,
        description=description,
        place=place,
        start_time=start_time,
        end_time=end_time,
        food=food,
        drinks=drinks,
        program=program,
        parking_info=parking_info,
        music=music,
        theme=theme,
        age_restrictions=age_restrictions,
        author_email=author_email
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def get_event(db: Session, event_id: int) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id).first()

def get_events(db: Session) -> List[Event]:
    """Get all events ordered by start time"""
    return db.query(Event).order_by(Event.start_time).all()

def get_upcoming_events(db: Session) -> List[Event]:
    """Get future events that haven't started yet"""
    now = datetime.now(UTC).replace(tzinfo=None)
    return (
        db.query(Event)
        .filter(Event.start_time > now)
        .order_by(Event.start_time)
        .all()
    )

def get_current_events(db: Session) -> List[Event]:
    """Get currently running events (started but not ended)"""
    now = datetime.now(UTC).replace(tzinfo=None)
    return (
        db.query(Event)
        .filter(Event.start_time <= now)
        .filter(Event.end_time > now)
        .order_by(Event.end_time)
        .all()
    )

def get_past_events(db: Session) -> List[Event]:
    """Get past events that have ended"""
    now = datetime.now(UTC).replace(tzinfo=None)
    return (
        db.query(Event)
        .filter(Event.end_time < now)
        .order_by(Event.end_time.desc())  # Most recent first
        .all()
    )

def get_user_events(db: Session, author_email: str) -> List[Event]:
    """Get all events by a specific user"""
    return (
        db.query(Event)
        .filter(Event.author_email == author_email)
        .order_by(Event.start_time)
        .all()
    )

def get_user_upcoming_events(db: Session, author_email: str) -> List[Event]:
    """Get future events by a specific user"""
    now = datetime.now(UTC).replace(tzinfo=None)
    return (
        db.query(Event)
        .filter(Event.author_email == author_email)
        .filter(Event.start_time > now)
        .order_by(Event.start_time)
        .all()
    )

def get_events_in_range(
    db: Session, 
    start_date: datetime, 
    end_date: datetime
) -> List[Event]:
    """Get events that start within a specific date range"""
    return (
        db.query(Event)
        .filter(Event.start_time >= start_date)
        .filter(Event.start_time <= end_date)
        .order_by(Event.start_time)
        .all()
    )

def update_event(
    db: Session,
    event_id: int,
    author_email: str,
    **kwargs
) -> Optional[Event]:
    event = get_event(db, event_id)
    if not event:
        raise ValueError("event not found")
    if event.author_email != author_email:
        raise ValueError("not authorized to update this event")
    
    try:
        # If updating times, validate them
        start_time = kwargs.get('start_time', event.start_time)
        end_time = kwargs.get('end_time', event.end_time)
        if 'start_time' in kwargs or 'end_time' in kwargs:
            validate_event_times(start_time, end_time)
        
        # Validate and normalize text fields
        for key, value in kwargs.items():
            if key in ['title', 'description', 'place', 'food', 'drinks', 
                      'program', 'parking_info', 'music', 'theme', 'age_restrictions']:
                if value is not None:
                    kwargs[key] = validate_text_field(key, value, required=key == 'title')
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        # Try to commit
        db.commit()
        db.refresh(event)
        return event
        
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to update event: {str(e)}")

def delete_event(db: Session, event_id: int, author_email: str) -> bool:
    event = get_event(db, event_id)
    if not event:
        raise ValueError("event not found")
    if event.author_email != author_email:
        raise ValueError("not authorized to delete this event")
    
    try:
        db.delete(event)
        db.commit()
        db.flush()  # Ensure changes are flushed to the database
        return True
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to delete event: {str(e)}")