import pytest
from playwright.sync_api import Page, TimeoutError
from test_helpers import create_test_users, create_test_event_data, PageHelper

@pytest.fixture
def logged_in_user1(page: Page) -> str:
    """Login as user1 before tests."""
    helper = PageHelper(page)
    users = create_test_users()
    helper.login(users["user1"])
    return users["user1"]

@pytest.fixture
def logged_in_user2(page: Page) -> str:
    """Login as user2 before tests."""
    helper = PageHelper(page)
    users = create_test_users()
    helper.login(users["user2"])
    return users["user2"]

def test_create_event(page: Page, logged_in_user1, screenshot_on_failure):
    """Test creating a new event."""
    helper = PageHelper(page)
    event_data = create_test_event_data()
    
    try:
        event_id = helper.create_event(event_data)
        assert event_id, "Event ID should be returned"
        
        # Verify event appears in list
        page.goto("/events")
        page.wait_for_load_state("networkidle")
        assert page.is_visible(f"text={event_data['title']}")
    except TimeoutError as e:
        pytest.fail(f"Create event test failed: {str(e)}")

def test_edit_event(page: Page, logged_in_user1, screenshot_on_failure):
    """Test editing an existing event."""
    helper = PageHelper(page)
    event_data = create_test_event_data()
    
    try:
        # Create event
        event_id = helper.create_event(event_data)
        
        # Edit event
        page.click("button:has-text('Edit')")
        updated_data = event_data.copy()
        updated_data["title"] = "Updated Test Event"
        helper.fill_event_form(updated_data)
        page.click("button:has-text('Update')")
        
        # Verify changes
        page.goto("/events")
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("mat-card", state="visible", timeout=5000)
        assert page.is_visible(f"text={updated_data['title']}")
    except TimeoutError as e:
        pytest.fail(f"Edit event test failed: {str(e)}")

def test_delete_event(page: Page, logged_in_user1, screenshot_on_failure):
    """Test deleting an event."""
    helper = PageHelper(page)
    event_data = create_test_event_data()
    
    try:
        # Create event
        event_id = helper.create_event(event_data)
        
        # Delete event
        page.click("button:has-text('Delete')")
        # Wait for dialog to appear and click Confirm
        page.wait_for_selector("mat-dialog-container", state="visible", timeout=5000)
        # Wait for dialog animation to complete
        page.wait_for_timeout(500)
        page.click("[data-test-id='confirm-dialog-confirm']")
        
        # Wait for dialog to close
        page.wait_for_selector("mat-dialog-container", state="hidden", timeout=5000)
        
        # Wait 500ms for delete request to originate
        page.wait_for_timeout(500)
        
        # Wait for all network requests to complete (delete request)
        page.wait_for_load_state("networkidle")
        
        # Wait 500ms for auto-navigation and new requests to originate
        # (component automatically navigates back to events list)
        page.wait_for_timeout(500)
        
        # Wait for all network requests to complete (auto-navigation)
        page.wait_for_load_state("networkidle")
        
        # Verify event is gone
        assert not page.is_visible(f"text={event_data['title']}")
    except TimeoutError as e:
        pytest.fail(f"Delete event test failed: {str(e)}")

def test_event_permissions(page: Page, logged_in_user2, screenshot_on_failure):
    """Test that non-owners cannot edit/delete events."""
    try:
        # Navigate to events list
        page.goto("/events")
        
        # Click first event (if any)
        if page.is_visible("mat-card"):
            page.click("mat-card >> nth=0")
            
            # Verify edit/delete not available
            assert not page.is_visible("button:has-text('Edit')")
            assert not page.is_visible("button:has-text('Delete')")
    except TimeoutError as e:
        pytest.fail(f"Event permissions test failed: {str(e)}")

def test_event_validation(page: Page, logged_in_user1, screenshot_on_failure):
    """Test event form validation."""
    try:
        # Navigate to create event
        page.click("button:has-text('Create Event')")
        
        # Check that submit button is disabled
        assert page.is_disabled("button:has-text('Create')")
        
        # Focus and blur the title field to trigger validation
        page.click("input[formControlName='title']")
        page.click("body")  # Click outside to trigger blur
        
        # Check validation errors
        assert page.is_visible("mat-error:has-text('Title is required')")
    except TimeoutError as e:
        pytest.fail(f"Event validation test failed: {str(e)}")

def test_event_listing_filters(page: Page, logged_in_user1, screenshot_on_failure):
    """Test event listing filters and sorting."""
    helper = PageHelper(page)
    event_data = create_test_event_data()
    
    try:
        # Create test event
        event_id = helper.create_event(event_data)
        
        # Test event list
        page.goto("/events")
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("mat-card", state="visible", timeout=5000)
        events_count = page.locator("mat-card").count()
        assert events_count > 0, "Should show at least one event"
        
        # Verify event details
        assert page.is_visible(f"text={event_data['title']}")
        assert page.is_visible(f"text={event_data['description']}")
        assert page.is_visible(f"text={event_data['place']}")
        
        # Verify event actions
        assert page.is_visible("button:has-text('View Details')")
        assert page.is_visible("button:has-text('Edit')")
        assert page.is_visible("button:has-text('Delete')")
    except TimeoutError as e:
        pytest.fail(f"Event listing filters test failed: {str(e)}")