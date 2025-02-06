from typing import List, Optional, Dict
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import EventComment, Event
import re

def validate_comment(
    db: Session,
    event_id: int,
    user_id: str,
    message: str,
    rating: int,
    check_existing: bool = True
) -> None:
    """Validate comment data"""
    # Check event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise ValueError("event not found")

    # Multiple comments per user are allowed

    # Validate message
    if not message or not message.strip():
        raise ValueError("message cannot be empty")
    if len(message) > 1000:  # Arbitrary limit
        raise ValueError("message too long (max 1000 characters)")
    
    # Remove any potentially harmful content
    if re.search(r"<[^>]*script|javascript:|onerror=|onclick=", message, re.I):
        raise ValueError("message contains invalid characters")

    # Validate rating
    if not isinstance(rating, int) or rating < 0 or rating > 5:
        raise ValueError("rating must be an integer between 0 and 5")

def create_comment(
    db: Session,
    event_id: int,
    user_id: str,
    message: str,
    rating: int = 0,
    author_email: str = None
) -> EventComment:
    # Validate comment data
    validate_comment(db, event_id, user_id, message, rating)
    
    # Create comment
    comment = EventComment(
        event_id=event_id,
        user_id=user_id,
        message=message.strip(),  # Normalize whitespace
        rating=rating,
        author_email=author_email or user_id
    )
    
    try:
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to create comment: {str(e)}")

def get_event_comments(db: Session, event_id: int) -> List[EventComment]:
    return db.query(EventComment).filter(EventComment.event_id == event_id).all()

def get_comment(db: Session, comment_id: int) -> Optional[EventComment]:
    return db.query(EventComment).filter(EventComment.id == comment_id).first()

def update_comment(
    db: Session,
    comment_id: int,
    author_email: str,
    message: Optional[str] = None,
    rating: Optional[int] = None
) -> Optional[EventComment]:
    comment = get_comment(db, comment_id)
    if not comment:
        raise ValueError("comment not found")
    if comment.author_email != author_email:
        raise ValueError("not authorized to update this comment")
    
    try:
        if message is not None:
            # Validate new message
            validate_comment(
                db, 
                comment.event_id, 
                comment.user_id, 
                message, 
                comment.rating,
                check_existing=False
            )
            comment.message = message.strip()
        
        if rating is not None:
            # Validate new rating
            validate_comment(
                db,
                comment.event_id,
                comment.user_id,
                comment.message,
                rating,
                check_existing=False
            )
            comment.rating = rating
        
        db.commit()
        db.refresh(comment)
        return comment
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to update comment: {str(e)}")

def get_event_rating_stats(db: Session, event_id: int) -> Dict:
    """Get rating statistics for an event"""
    # Get all ratings
    ratings = (
        db.query(EventComment.rating)
        .filter(EventComment.event_id == event_id)
        .all()
    )
    
    if not ratings:
        return {
            "average_rating": 0,
            "total_ratings": 0,
            "rating_distribution": {i: 0 for i in range(1, 6)}
        }
    
    # Calculate statistics
    ratings = [r[0] for r in ratings]
    distribution = {i: ratings.count(i) for i in range(1, 6)}
    
    return {
        "average_rating": sum(ratings) / len(ratings),
        "total_ratings": len(ratings),
        "rating_distribution": distribution
    }

def get_comment_history(db: Session, comment_id: int) -> List[Dict]:
    """Get edit history of a comment"""
    # Note: This is a stub since we don't actually store history
    # In a real implementation, we would have a CommentHistory table
    comment = get_comment(db, comment_id)
    if not comment:
        return []
    
    return [{
        "message": comment.message,
        "rating": comment.rating,
        "timestamp": datetime.now(UTC)  # This would be the actual edit timestamp
    }]

def delete_comment(db: Session, comment_id: int, author_email: str) -> bool:
    comment = get_comment(db, comment_id)
    if not comment:
        raise ValueError("comment not found")
    if comment.author_email != author_email:
        raise ValueError("not authorized to delete this comment")
    
    try:
        db.delete(comment)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to delete comment: {str(e)}")