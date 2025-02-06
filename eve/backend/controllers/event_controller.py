from datetime import datetime, UTC
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from database import get_db
from use_cases import auth_use_cases, event_use_cases

router = APIRouter(prefix="/api/events", tags=["events"])

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    place: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    food: Optional[str] = None
    drinks: Optional[str] = None
    program: Optional[str] = None
    parking_info: Optional[str] = None
    music: Optional[str] = None
    theme: Optional[str] = None
    age_restrictions: Optional[str] = None

    @field_validator('start_time', 'end_time', mode='before')
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    author_email: str

    class Config:
        from_attributes = True

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_id = request.headers.get("Authorization")
    if not session_id:
        raise HTTPException(status_code=401, detail="Authorization header required")
    is_valid, email = auth_use_cases.validate_session(db, session_id)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return email

@router.post("", response_model=EventResponse)
def create_event(event: EventCreate, 
                db: Session = Depends(get_db),
                current_user: str = Depends(get_current_user)):
    return event_use_cases.create_event(
        db=db,
        author_email=current_user,
        **event.model_dump()
    )

@router.get("", response_model=List[EventResponse])
def list_events(db: Session = Depends(get_db),
                current_user: str = Depends(get_current_user)):
    return event_use_cases.get_events(db)

@router.get("/my", response_model=List[EventResponse])
def list_my_events(db: Session = Depends(get_db),
                  current_user: str = Depends(get_current_user)):
    all_events = event_use_cases.get_events(db)
    return [event for event in all_events if event.author_email == current_user]

@router.get("/upcoming", response_model=List[EventResponse])
def list_upcoming_events(db: Session = Depends(get_db),
                        current_user: str = Depends(get_current_user)):
    all_events = event_use_cases.get_events(db)
    # Compare naive UTC datetimes
    now = datetime.now(UTC).replace(tzinfo=None)
    return [event for event in all_events if event.start_time > now]

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int,
              db: Session = Depends(get_db),
              current_user: str = Depends(get_current_user)):
    event = event_use_cases.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/{event_id}", response_model=EventResponse)
def update_event(event_id: int,
                event: EventCreate,
                db: Session = Depends(get_db),
                current_user: str = Depends(get_current_user)):
    try:
        updated_event = event_use_cases.update_event(
            db=db,
            event_id=event_id,
            author_email=current_user,
            **event.model_dump()
        )
        return updated_event
    except ValueError as e:
        if "not authorized" in str(e):
            raise HTTPException(status_code=403, detail="not authorized to update this event")
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="Event not found")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{event_id}")
def delete_event(event_id: int,
                db: Session = Depends(get_db),
                current_user: str = Depends(get_current_user)):
    try:
        event_use_cases.delete_event(db, event_id, current_user)
        return {"message": "Event deleted successfully"}
    except ValueError as e:
        if "not authorized" in str(e):
            raise HTTPException(status_code=403, detail="not authorized to delete this event")
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="Event not found")
        raise HTTPException(status_code=400, detail=str(e))