import pytest
from playwright.sync_api import Page, TimeoutError
from test_helpers import create_test_users, create_test_event_data, PageHelper, dump_html

@pytest.fixture
def event_with_comment(page: Page):
    """Create an event and add a comment to it."""
    helper = PageHelper(page)
    users = create_test_users()
    event_data = create_test_event_data()
    
    try:
        # Login as user1 and create event
        helper.login(users["user1"])
        event_id = helper.create_event(event_data)
        
        # Switch to user2 and add comment
        helper.logout()
        helper.login(users["user2"])
        
        page.goto(f"/events/{event_id}")
        page.wait_for_load_state("networkidle")
        helper.add_comment("Test comment", rating=5)
        
        return {
            "event_id": event_id,
            "comment_text": "Test comment",
            "user1": users["user1"],
            "user2": users["user2"]
        }
    except TimeoutError as e:
        pytest.fail(dump_html(page, f"Event with comment fixture failed: {str(e)}"))

def test_add_comment(page: Page, event_with_comment, screenshot_on_failure):
    """Test adding a comment to an event."""
    try:
        page.goto(f"/events/{event_with_comment['event_id']}")
        page.wait_for_load_state("networkidle")
        page.wait_for_selector(f"text={event_with_comment['comment_text']}", state="visible", timeout=10000)
    except TimeoutError as e:
        pytest.fail(dump_html(page, f"Add comment test failed: {str(e)}"))

def test_edit_comment(page: Page, event_with_comment, screenshot_on_failure):
    """Test editing a comment."""
    helper = PageHelper(page)
    new_message = "Updated test comment"
    
    try:
        # Login as comment author
        helper.login(event_with_comment["user2"])
        
        page.goto(f"/events/{event_with_comment['event_id']}")
        comment = page.locator(f".comment-item:has-text('{event_with_comment['comment_text']}')")
        
        # Edit comment
        comment.locator("button:has-text('Edit')").click()
        page.fill("textarea[formControlName='message']", new_message)
        page.click("mat-radio-button[value='4']")
        page.click("button:has-text('Save')")
        
        # Verify changes
        assert page.is_visible(f"text={new_message}")
        assert page.is_visible("text=Rating: 4")
    except TimeoutError as e:
        pytest.fail(dump_html(page, f"Edit comment test failed: {str(e)}"))

def test_delete_comment(page: Page, event_with_comment, screenshot_on_failure):
    """Test deleting a comment."""
    helper = PageHelper(page)
    
    try:
        # Login as comment author
        helper.login(event_with_comment["user2"])
        
        page.goto(f"/events/{event_with_comment['event_id']}")
        comment = page.locator(f".comment-item:has-text('{event_with_comment['comment_text']}')")
        
        # Delete comment
        comment.locator("button:has-text('Delete')").click()
        page.click("button:has-text('Confirm')")
        
        # Verify comment is gone
        assert not page.is_visible(f"text={event_with_comment['comment_text']}")
    except TimeoutError as e:
        pytest.fail(dump_html(page, f"Delete comment test failed: {str(e)}"))

def test_comment_permissions(page: Page, event_with_comment, screenshot_on_failure):
    """Test that only comment authors can edit/delete their comments."""
    helper = PageHelper(page)
    
    try:
        # Login as event creator (not comment author)
        helper.login(event_with_comment["user1"])
        
        page.goto(f"/events/{event_with_comment['event_id']}")
        comment = page.locator(f".comment-item:has-text('{event_with_comment['comment_text']}')")
        
        # Verify edit/delete not available
        assert not comment.is_visible("button:has-text('Edit')")
        assert not comment.is_visible("button:has-text('Delete')")
        
        # Switch to comment author
        helper.logout()
        helper.login(event_with_comment["user2"])
        
        page.goto(f"/events/{event_with_comment['event_id']}")
        comment = page.locator(f".comment-item:has-text('{event_with_comment['comment_text']}')")
        
        # Verify edit/delete available
        assert comment.is_visible("button:has-text('Edit')")
        assert comment.is_visible("button:has-text('Delete')")
    except TimeoutError as e:
        pytest.fail(dump_html(page, f"Comment permissions test failed: {str(e)}"))