#!/usr/bin/env python3
import os
import sys
import json
import time
import signal
import subprocess
import requests
from datetime import datetime, timedelta, UTC
from typing import Optional

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)

from sqlalchemy import create_engine
from backend.models import Base

# Ensure we're in the correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:2021"

def print_step(message):
    print("\n" + "="*80)
    print(message)
    print("="*80)

def print_response_error(response):
    print(f"Status code: {response.status_code}")
    try:
        print(f"Error: {response.json()}")
    except:
        print(f"Error: {response.text}")

def cleanup_database():
    """Clean up database tables but keep the file"""
    try:
        engine = create_engine("sqlite:///data/eve.db")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Database cleanup failed: {e}")
        return False

def start_server():
    """Start the backend server."""
    server_process = subprocess.Popen(
        ["bash", "-c", "PYTHONPATH=backend python backend/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    return server_process

def cleanup_server(server_process):
    """Clean up server and its resources"""
    if server_process:
        try:
            # First kill the process group
            try:
                os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
            except ProcessLookupError:
                # Process already terminated
                pass
            
            # Now we can safely get the output
            stdout, stderr = server_process.communicate(timeout=5)  # 5 second timeout
            return stdout, stderr
        except Exception as e:
            print(f"Warning: Error during server cleanup: {e}")
            # Force kill if needed
            try:
                os.killpg(os.getpgid(server_process.pid), signal.SIGKILL)
            except:
                pass
    return None, None

def wait_for_server(url: str, max_retries: int = 30, delay: float = 0.5) -> bool:
    """Wait for the server to become available."""
    for _ in range(max_retries):
        try:
            response = requests.get(f"{url}/docs")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(delay)
    return False

def main():
    server_process = None
    test_failed = False
    stdout = stderr = None
    try:
        # Clean up database
        if not cleanup_database():
            print("Failed to clean database")
            sys.exit(1)
        
        # Start server
        print("Starting server...")
        server_process = start_server()
        
        # Wait for server to start
        if not wait_for_server(BASE_URL):
            print("Error: Server did not start in time")
            sys.exit(1)
        print("Server started successfully")

        # Test user credentials
        user1_email = "user1@example.com"
        user2_email = "user2@example.com"

        print_step("1. Testing Authentication")
        # Login user1
        print("Logging in user1...")
        response = requests.post(f"{BASE_URL}/api/auth/login", json={"email": user1_email})
        assert response.status_code == 200
        user1_session = response.json()["session_id"]
        print(f"User1 session: {user1_session}")

        # Login user2
        print("Logging in user2...")
        response = requests.post(f"{BASE_URL}/api/auth/login", json={"email": user2_email})
        assert response.status_code == 200
        user2_session = response.json()["session_id"]
        print(f"User2 session: {user2_session}")

        print_step("2. Testing Event Creation")
        # Create event as user1
        event_data = {
            "title": "Summer Party",
            "description": "Amazing summer party",
            "place": "Beach Club",
            "start_time": (datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None).isoformat(),
            "end_time": (datetime.now(UTC) + timedelta(days=1, hours=4)).replace(tzinfo=None).isoformat(),
            "food": "BBQ",
            "drinks": "Cocktails",
            "program": "Dancing and games",
            "parking_info": "Free parking available",
            "music": "Live DJ",
            "theme": "Summer vibes",
            "age_restrictions": "18+"
        }
        
        print("Creating event as user1...")
        print("Event data:", event_data)
        response = requests.post(
            f"{BASE_URL}/api/events",
            headers={"Authorization": user1_session},
            json=event_data
        )
        print("Response:", response.status_code)
        if response.status_code != 200:
            print("Error:", response.text)
        assert response.status_code == 200
        event = response.json()
        event_id = event["id"]
        print(f"Created event with ID: {event_id}")

        print_step("3. Testing Event Listing")
        print("Getting all events...")
        response = requests.get(
            f"{BASE_URL}/api/events",
            headers={"Authorization": user1_session}
        )
        assert response.status_code == 200
        events = response.json()
        print(f"Found {len(events)} events")

        print("\nGetting upcoming events...")
        response = requests.get(
            f"{BASE_URL}/api/events/upcoming",
            headers={"Authorization": user1_session}
        )
        assert response.status_code == 200
        upcoming_events = response.json()
        print(f"Found {len(upcoming_events)} upcoming events")

        print_step("4. Testing Comments")
        # Add comment as user2
        comment_data = {
            "message": "Looking forward to it!",
            "rating": 5
        }
        
        print("Adding comment as user2...")
        response = requests.post(
            f"{BASE_URL}/api/events/{event_id}/comments",
            headers={"Authorization": user2_session},
            json=comment_data
        )
        assert response.status_code == 200
        comment = response.json()
        comment_id = comment["id"]
        print(f"Created comment with ID: {comment_id}")

        # Get comments
        print("\nGetting event comments...")
        response = requests.get(
            f"{BASE_URL}/api/events/{event_id}/comments",
            headers={"Authorization": user1_session}
        )
        assert response.status_code == 200
        comments = response.json()
        print(f"Found {len(comments)} comments")

        print_step("5. Testing Event Update")
        # Update event as owner (user1)
        update_data = event_data.copy()
        update_data["title"] = "Updated Summer Party"
        
        print("Updating event as owner...")
        response = requests.put(
            f"{BASE_URL}/api/events/{event_id}",
            headers={"Authorization": user1_session},
            json=update_data
        )
        assert response.status_code == 200
        updated_event = response.json()
        print(f"Updated event title: {updated_event['title']}")

        # Try to update event as non-owner (user2)
        print("\nTrying to update event as non-owner...")
        response = requests.put(
            f"{BASE_URL}/api/events/{event_id}",
            headers={"Authorization": user2_session},
            json=update_data
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("Update failed with authorization error as expected")

        print_step("6. Testing Cleanup")
        # Delete event as owner
        print("Deleting event as owner...")
        response = requests.delete(
            f"{BASE_URL}/api/events/{event_id}",
            headers={"Authorization": user1_session}
        )
        assert response.status_code == 200
        print("Event deleted successfully")

        # Verify event is gone
        print("\nVerifying event deletion...")
        response = requests.get(
            f"{BASE_URL}/api/events/{event_id}",
            headers={"Authorization": user1_session}
        )
        assert response.status_code == 404
        print("Event not found as expected")

        print_step("All tests passed successfully!")
    
    except Exception as e:
        test_failed = True
        print(f"\nTest Error: {str(e)}")
        if isinstance(e, requests.exceptions.RequestException) and hasattr(e, 'response'):
            print_response_error(e.response)
    finally:
        if server_process:
            stdout, stderr = cleanup_server(server_process)
            print("Server stopped")
            if test_failed and stdout and stderr:
                print("\nServer stdout:", stdout.decode())
                print("\nServer stderr:", stderr.decode())
        if test_failed:
            sys.exit(1)

if __name__ == "__main__":
    main()