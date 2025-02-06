from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    place = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=True)  # Stored as UTC
    end_time = Column(DateTime, nullable=True)  # Stored as UTC

    @property
    def start_time_utc(self):
        return self.start_time.replace(tzinfo=UTC) if self.start_time else None

    @property
    def end_time_utc(self):
        return self.end_time.replace(tzinfo=UTC) if self.end_time else None
    food = Column(String)
    drinks = Column(String)
    program = Column(String)
    parking_info = Column(String)
    music = Column(String)
    theme = Column(String)
    age_restrictions = Column(String)
    author_email = Column(String, nullable=False)
    
    comments = relationship("EventComment", back_populates="event", cascade="all, delete-orphan")

class EventComment(Base):
    __tablename__ = 'event_comments'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String, nullable=False)  # user's email
    message = Column(String, nullable=False)
    rating = Column(Integer, default=0)
    author_email = Column(String, nullable=False)
    
    event = relationship("Event", back_populates="comments")

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(String, primary_key=True)  # UUID
    user_email = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))  # Stored as UTC
    expires_at = Column(DateTime, nullable=False)  # Stored as UTC

    @property
    def created_at_utc(self):
        return self.created_at.replace(tzinfo=UTC) if self.created_at else None

    @property
    def expires_at_utc(self):
        return self.expires_at.replace(tzinfo=UTC) if self.expires_at else None