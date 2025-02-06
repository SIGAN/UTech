from datetime import datetime, timedelta, UTC
import uuid
from sqlalchemy.orm import Session
from models import Session as DbSession

def create_session(db: Session, email: str) -> str:
    session_id = str(uuid.uuid4())
    # Store naive UTC datetime in database
    expires_at = (datetime.now(UTC) + timedelta(hours=8)).replace(tzinfo=None)
    
    db_session = DbSession(
        id=session_id,
        user_email=email,
        created_at=datetime.now(UTC).replace(tzinfo=None),
        expires_at=expires_at
    )
    
    db.add(db_session)
    db.commit()
    return session_id

def validate_session(db: Session, session_id: str) -> tuple[bool, str | None]:
    session = db.query(DbSession).filter(DbSession.id == session_id).first()
    if not session:
        return False, None
    
    # Compare naive UTC datetimes
    if session.expires_at < datetime.now(UTC).replace(tzinfo=None):
        db.delete(session)
        db.commit()
        return False, None
    
    return True, session.user_email

def logout(db: Session, session_id: str):
    session = db.query(DbSession).filter(DbSession.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()