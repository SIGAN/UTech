import pytest
import time
from playwright.sync_api import Page, TimeoutError
from test_helpers import PageHelper, create_test_users

def test_new_user_login(page: Page, screenshot_on_failure):
    """Test that a new user can login with a non-existent email."""
    helper = PageHelper(page)
    users = create_test_users()  # Get test users for later use
    # Use timestamp to ensure unique email for each test run
    new_email = f"new.user.{int(time.time())}@example.com"  # Email that doesn't exist in test_users
    
    try:
        helper.login(new_email)
        # Should successfully log in and show My Events
        assert page.is_visible("text=My Events"), "New user should be able to login and see My Events"
        
        # Verify we can create events with this new user
        page.click("button:has-text('Create Event')")
        assert page.is_visible("text=Create New Event"), "New user should be able to access event creation"
        
        # Go back to events page
        page.click("button:has-text('Cancel')")
        page.wait_for_selector("text=My Events")
        
        # Logout and verify we can log back in
        helper.logout()
        helper.login(new_email)
        assert page.is_visible("text=My Events"), "Should be able to login again with the same email"
        
        # Finally, logout and login as the standard test user for subsequent tests
        helper.logout()
        helper.login(users["user1"])
        assert page.is_visible("text=My Events"), "Should be able to login as standard test user"
    except TimeoutError as e:
        pytest.fail(f"New user login test failed: {str(e)}")
    finally:
        # Even if test fails, try to ensure we're logged in as standard test user
        try:
            helper.logout()
            helper.login(users["user1"])
        except:
            pass