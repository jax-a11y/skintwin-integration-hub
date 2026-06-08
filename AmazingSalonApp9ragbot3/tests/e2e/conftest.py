"""
E2E test configuration for Playwright.
"""
import os
import pytest

# Base URL for tests
BASE_URL = os.environ.get('E2E_BASE_URL', 'http://127.0.0.1:5000')

# Test credentials
TEST_ADMIN_EMAIL = 'admin@test.com'
TEST_ADMIN_PASSWORD = 'TestPassword123!'


@pytest.fixture(scope="session")
def base_url():
    """Get base URL for tests."""
    return BASE_URL


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch args."""
    return {
        **browser_type_launch_args,
        "headless": True,
        "slow_mo": 0,
    }


@pytest.fixture
def logged_in_admin(page, base_url):
    """Login as admin and return page."""
    page.goto(f"{base_url}/auth/login")
    page.wait_for_load_state('networkidle')
    
    # Fill login form
    email_field = page.locator('input[name="email"], input[type="email"]')
    password_field = page.locator('input[name="password"], input[type="password"]')
    submit_btn = page.locator('button[type="submit"], input[type="submit"]')
    
    if email_field.count() > 0:
        email_field.fill(TEST_ADMIN_EMAIL)
    if password_field.count() > 0:
        password_field.fill(TEST_ADMIN_PASSWORD)
    if submit_btn.count() > 0:
        submit_btn.first.click()
    
    page.wait_for_load_state('networkidle')
    
    return page


@pytest.fixture
def logged_in_user(page, base_url):
    """Login as regular user and return page."""
    page.goto(f"{base_url}/auth/login")
    page.wait_for_load_state('networkidle')
    
    email_field = page.locator('input[name="email"], input[type="email"]')
    password_field = page.locator('input[name="password"], input[type="password"]')
    submit_btn = page.locator('button[type="submit"], input[type="submit"]')
    
    if email_field.count() > 0:
        email_field.fill('user@test.com')
    if password_field.count() > 0:
        password_field.fill(TEST_ADMIN_PASSWORD)
    if submit_btn.count() > 0:
        submit_btn.first.click()
    
    page.wait_for_load_state('networkidle')
    
    return page
