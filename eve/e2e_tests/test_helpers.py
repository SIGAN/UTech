from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional
from playwright.sync_api import Page, TimeoutError

def create_test_event_data() -> Dict[str, Any]:
    """Create test event data with all fields."""
    start_time = datetime.now(UTC) + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)
    
    return {
        "title": "Test Event",
        "description": "This is a test event description",
        "place": "Test Venue",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "food": "Test Food",
        "drinks": "Test Drinks",
        "program": "Test Program Details",
        "parking_info": "Test Parking Information",
        "music": "Test Music",
        "theme": "Test Theme",
        "age_restrictions": "18+"
    }

def create_test_users() -> Dict[str, str]:
    """Create test user data."""
    return {
        "user1": "test1@example.com",
        "user2": "test2@example.com"
    }

def assert_event_data_matches(actual: Dict[str, Any], expected: Dict[str, Any]) -> None:
    """Assert that actual event data matches expected data."""
    for key in expected:
        if key in ["start_time", "end_time"]:
            # Skip date/time validation
            continue
        else:
            assert actual[key] == expected[key], f"Mismatch in {key}"

def dump_html(page: Page, error_msg: str) -> str:
    """Dump HTML content of the main container and return error message with HTML."""
    try:
        # Try to get the main container content first
        container = page.locator("mat-sidenav-content").first
        html_content = container.inner_html() if container else page.content()
    except:
        # Fallback to full page content if container not found
        html_content = page.content()
    return f"{error_msg}\nCurrent container HTML:\n{html_content}"

class PageHelper:
    """Helper class for common page operations."""
    TIMEOUT = 10000  # 10 seconds timeout for all operations
    def __init__(self, page: Page):
        self.page = page
        
    def remove_webpack_overlay(self):
        """Remove webpack dev server overlay if present."""
        self.page.evaluate("""
            const overlay = document.getElementById('webpack-dev-server-client-overlay');
            if (overlay) overlay.remove();
        """)

    def login(self, email: str) -> None:
        """Login with the given email."""
        try:
            # Go to login page first to ensure we have access to localStorage
            self.page.goto("/login")
            self.page.wait_for_load_state("networkidle")
            
            # Clear any existing session
            self.page.evaluate("localStorage.clear()")
            self.remove_webpack_overlay()
            
            # Fill and submit login form
            self.page.fill("input[type='email']", email)
            self.page.click("button:has-text('Login')")
            
            # Wait for successful login
            self.page.wait_for_selector("text=My Events", state="visible", timeout=self.TIMEOUT)
            
            # Wait for session ID to be set in localStorage
            session_id = None
            for _ in range(5):  # Try up to 5 times
                session_id = self.page.evaluate("localStorage.getItem('sessionId')")
                if session_id:
                    break
                print(f"Waiting for session ID... Current localStorage: {self.page.evaluate('JSON.stringify(localStorage)')}")
                self.page.wait_for_timeout(1000)  # Wait 1 second between attempts
            
            if not session_id:
                # Try to get the response from the login request
                response = self.page.request.post(
                    "http://localhost:2021/api/auth/login",
                    data={"email": email},
                    headers={"Content-Type": "application/json"}
                )
                print(f"Login response: {response.text()}")
                raise TimeoutError("Failed to get session ID from localStorage")
            
            # Reload the page to ensure the session is properly set
            self.page.reload()
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_selector("text=My Events", state="visible", timeout=self.TIMEOUT)
        except TimeoutError:
            raise TimeoutError(dump_html(self.page, f"Login failed for {email}"))

    def logout(self) -> None:
        """Logout the current user."""
        try:
            # First go to events page where logout button is always visible
            self.page.goto("/events")
            self.page.wait_for_load_state("networkidle")
            self.page.click("button:has-text('Logout')")
            self.page.wait_for_selector("text=Login")
        except TimeoutError:
            raise TimeoutError("Logout failed")

    def create_event(self, event_data: Dict[str, Any]) -> str:
        """Create a new event and return its ID."""
        try:
            self.page.goto("/events")
            self.page.wait_for_load_state("networkidle")
            self.remove_webpack_overlay()
            
            self.page.wait_for_selector("button:has-text('Create Event')", state="visible", timeout=self.TIMEOUT)
            self.page.click("button:has-text('Create Event')")
            self.fill_event_form(event_data)
            
            # Wait for Create button to be enabled
            self.page.wait_for_selector("button:has-text('Create'):not([disabled])", state="visible", timeout=self.TIMEOUT)
            self.page.click("button:has-text('Create')")
            
            # Wait for redirect and get event ID from URL
            self.page.wait_for_url(lambda url: "/events/" in url)
            event_id = self.page.url.split("/")[-1]
            
            # Go back to events list and wait for card to appear
            self.page.goto("/events")
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_selector("mat-card", state="visible", timeout=self.TIMEOUT)
            
            return event_id
        except TimeoutError:
            raise TimeoutError(dump_html(self.page, "Event creation failed"))

    def fill_event_form(self, event_data: Dict[str, Any]) -> None:
        """Fill out the event form."""
        try:
            self.page.wait_for_selector("input[formControlName='title']", state="visible", timeout=self.TIMEOUT)
            
            # Fill the form
            self.page.fill("input[formControlName='title']", event_data["title"])
            
            # Optional fields
            if "description" in event_data:
                self.page.fill("textarea[formControlName='description']", event_data["description"])
            if "place" in event_data:
                self.page.fill("input[formControlName='place']", event_data["place"])
            
            # Convert datetime to string format expected by the input
            if "start_time" in event_data:
                start_time = datetime.fromisoformat(event_data["start_time"])
                self.page.fill("input[formControlName='start_date']", start_time.strftime("%Y-%m-%d"))
                self.page.fill("input[formControlName='start_time']", start_time.strftime("%H:%M"))
            
            if "end_time" in event_data:
                end_time = datetime.fromisoformat(event_data["end_time"])
                self.page.fill("input[formControlName='end_date']", end_time.strftime("%Y-%m-%d"))
                self.page.fill("input[formControlName='end_time']", end_time.strftime("%H:%M"))
            
            # Optional fields
            for field in ["food", "drinks", "parking_info", "music", "theme", "age_restrictions"]:
                if field in event_data:
                    self.page.fill(f"input[formControlName='{field}']", event_data[field])
            
            # Program is a textarea
            if "program" in event_data:
                self.page.fill("textarea[formControlName='program']", event_data["program"])
            
            # Wait for the form to be valid
            self.page.wait_for_selector("button[type='submit']:not([disabled])", state="visible", timeout=self.TIMEOUT)
        except TimeoutError:
            raise TimeoutError(dump_html(self.page, "Failed to fill event form"))

    def add_comment(self, message: str, rating: int = 0) -> str:
        """Add a comment and return its ID."""
        try:
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_selector("textarea[formControlName='message']", state="visible", timeout=self.TIMEOUT)
            self.page.fill("textarea[formControlName='message']", message)
            if rating > 0:
                self.page.wait_for_selector(f"mat-radio-button[value='{rating}']", state="visible", timeout=self.TIMEOUT)
                self.page.click(f"mat-radio-button[value='{rating}']")
            self.page.wait_for_selector("button:has-text('Add Comment')", state="visible", timeout=self.TIMEOUT)
            self.page.click("button:has-text('Add Comment')")
            
            # Wait for comment to appear and get its ID
            comment = self.page.wait_for_selector(f".comment-item:has-text('{message}')", state="visible", timeout=self.TIMEOUT)
            return comment.get_attribute("data-comment-id")
        except TimeoutError:
            raise TimeoutError(dump_html(self.page, "Failed to add comment"))