#!/usr/bin/env python3
import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from controllers import auth_controller, event_controller, comment_controller
from database import init_db

# Ensure we're in the correct working directory
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Eve Event Planner API")

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    status_code = 403 if "not authorized" in str(exc) else 400
    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc)},
    )

@app.options("/{path:path}")
async def options_handler():
    return {"message": "OK"}

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600  # Cache preflight requests for 1 hour
)

# Include routers
app.include_router(auth_controller.router)
app.include_router(event_controller.router)
app.include_router(comment_controller.router)

# Initialize database
init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2021)