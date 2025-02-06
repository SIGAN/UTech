from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from use_cases import auth_use_cases

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: EmailStr

class LoginResponse(BaseModel):
    session_id: str

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    session_id = auth_use_cases.create_session(db, request.email)
    return {"session_id": session_id}

@router.post("/logout", status_code=204)
def logout(session_id: str = Depends(lambda x: x.headers.get("Authorization")), 
          db: Session = Depends(get_db)):
    auth_use_cases.logout(db, session_id)
    return None