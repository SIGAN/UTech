import pytest
from playwright.sync_api import Page, TimeoutError
from test_helpers import create_test_users, PageHelper

def test_login_success(page: Page, screenshot_on_failure):
    """Test successful login."""
    helper = PageHelper(page)
    users = create_test_users()
    
    try:
        helper.login(users["user1"])
        assert page.is_visible("text=My Events")
    except TimeoutError as e:
        pytest.fail(f"Login test failed: {str(e)}")

def test_login_persistence(page: Page, screenshot_on_failure):
    """Test that login session persists after page reload."""
    helper = PageHelper(page)
    users = create_test_users()
    
    try:
        helper.login(users["user1"])
        page.reload()
        assert page.is_visible("text=My Events")
    except TimeoutError as e:
        pytest.fail(f"Login persistence test failed: {str(e)}")

def test_logout(page: Page, screenshot_on_failure):
    """Test logout functionality."""
    helper = PageHelper(page)
    users = create_test_users()
    
    try:
        helper.login(users["user1"])
        helper.logout()
        assert page.is_visible("text=Login")
    except TimeoutError as e:
        pytest.fail(f"Logout test failed: {str(e)}")

def test_invalid_email(page: Page, screenshot_on_failure):
    """Test login with invalid email format."""
    try:
        page.goto("/login")
        page.fill("input[type='email']", "invalid-email")
        # Trigger validation by clicking outside the input
        page.click("mat-card")
        
        # The button should be disabled and there should be a validation error
        assert page.get_attribute("button:has-text('Login')", "disabled") == "true"
        error = page.wait_for_selector("mat-error")
        assert "valid email" in error.text_content().lower()
    except TimeoutError as e:
        pytest.fail(f"Invalid email test failed: {str(e)}")