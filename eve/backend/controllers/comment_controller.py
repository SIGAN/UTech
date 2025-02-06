from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from use_cases import auth_use_cases, comment_use_cases

router = APIRouter(tags=["comments"])

class CommentBase(BaseModel):
    message: str
    rating: int = 0

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    event_id: int
    user_id: str
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

@router.get("/api/events/{event_id}/comments", response_model=List[CommentResponse])
def list_comments(event_id: int,
                 db: Session = Depends(get_db),
                 current_user: str = Depends(get_current_user)):
    return comment_use_cases.get_event_comments(db, event_id)

@router.post("/api/events/{event_id}/comments", response_model=CommentResponse)
def create_comment(event_id: int,
                  comment: CommentCreate,
                  db: Session = Depends(get_db),
                  current_user: str = Depends(get_current_user)):
    return comment_use_cases.create_comment(
        db=db,
        event_id=event_id,
        user_id=current_user,
        author_email=current_user,
        **comment.model_dump()
    )

@router.put("/api/events/{event_id}/comments/{comment_id}", response_model=CommentResponse)
def update_comment(event_id: int,
                  comment_id: int,
                  comment: CommentCreate,
                  db: Session = Depends(get_db),
                  current_user: str = Depends(get_current_user)):
    try:
        updated_comment = comment_use_cases.update_comment(
            db=db,
            comment_id=comment_id,
            author_email=current_user,
            **comment.model_dump()
        )
        return updated_comment
    except ValueError as e:
        if "not authorized" in str(e):
            raise HTTPException(status_code=403, detail="not authorized to update this comment")
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="Comment not found")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api/events/{event_id}/comments/{comment_id}")
def delete_comment(event_id: int,
                  comment_id: int,
                  db: Session = Depends(get_db),
                  current_user: str = Depends(get_current_user)):
    try:
        comment_use_cases.delete_comment(db, comment_id, current_user)
        return {"message": "Comment deleted successfully"}
    except ValueError as e:
        if "not authorized" in str(e):
            raise HTTPException(status_code=403, detail="not authorized to delete this comment")
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="Comment not found")
        raise HTTPException(status_code=400, detail=str(e))