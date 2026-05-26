"""
E2E Test fixtures and helpers for Playwright tests.
"""
import os
import pytest
from typing import Generator


# Base URL for the app
BASE_URL = os.environ.get('E2E_BASE_URL', 'http://127.0.0.1:5000')

# Test credentials
TEST_ADMIN_EMAIL = 'admin@test.com'
TEST_ADMIN_PASSWORD = 'TestPassword123!'
TEST_USER_EMAIL = 'user@test.com'
TEST_USER_PASSWORD = 'TestPassword123!'


@pytest.fixture(scope="session")
def base_url():
    """Get base URL for tests."""
    return BASE_URL


@pytest.fixture
def auth_page(page, base_url):
    """Navigate to login page."""
    page.goto(f"{base_url}/auth/login")
    return page


@pytest.fixture
def logged_in_admin(page, base_url):
    """Login as admin and return page."""
    page.goto(f"{base_url}/auth/login")
    
    # Fill login form
    page.fill('input[name="email"]', TEST_ADMIN_EMAIL)
    page.fill('input[name="password"]', TEST_ADMIN_PASSWORD)
    page.click('button[type="submit"]')
    
    # Wait for navigation
    page.wait_for_load_state('networkidle')
    
    return page


@pytest.fixture
def logged_in_user(page, base_url):
    """Login as regular user and return page."""
    page.goto(f"{base_url}/auth/login")
    
    # Fill login form
    page.fill('input[name="email"]', TEST_USER_EMAIL)
    page.fill('input[name="password"]', TEST_USER_PASSWORD)
    page.click('button[type="submit"]')
    
    # Wait for navigation
    page.wait_for_load_state('networkidle')
    
    return page


class PageHelpers:
    """Helper methods for page interactions."""
    
    def __init__(self, page):
        self.page = page
    
    def wait_for_toast(self, timeout=5000):
        """Wait for toast notification to appear."""
        try:
            self.page.wait_for_selector('.toast, .alert, .flash-message', timeout=timeout)
            return True
        except:
            return False
    
    def get_toast_message(self):
        """Get text from toast notification."""
        toast = self.page.query_selector('.toast, .alert, .flash-message')
        return toast.text_content() if toast else None
    
    def is_logged_in(self):
        """Check if user is logged in."""
        # Look for logout link or user menu
        return self.page.query_selector('a[href*="logout"], .user-menu, .logout-btn') is not None
    
    def take_screenshot(self, name):
        """Take a screenshot with given name."""
        os.makedirs('test-results/screenshots', exist_ok=True)
        self.page.screenshot(path=f'test-results/screenshots/{name}.png')
    
    def fill_form(self, fields: dict):
        """Fill form fields."""
        for selector, value in fields.items():
            self.page.fill(selector, value)
    
    def select_option(self, selector, value):
        """Select option from dropdown."""
        self.page.select_option(selector, value)
    
    def click_and_wait(self, selector, wait_for='networkidle'):
        """Click element and wait for network."""
        self.page.click(selector)
        self.page.wait_for_load_state(wait_for)


@pytest.fixture
def helpers(page):
    """Get page helpers."""
    return PageHelpers(page)


# Test data generators
def generate_client_data(index=1):
    """Generate test client data."""
    return {
        'name': f'E2E Test Client {index}',
        'email': f'e2e-client-{index}@test.com',
        'phone': f'555-E2E-{index:04d}',
    }


def generate_appointment_data():
    """Generate test appointment data."""
    from datetime import datetime, timedelta
    future_date = datetime.now() + timedelta(days=7)
    return {
        'date': future_date.strftime('%Y-%m-%d'),
        'time': '10:00',
        'notes': 'E2E test appointment',
    }


def generate_service_data(index=1):
    """Generate test service data."""
    return {
        'name': f'E2E Test Service {index}',
        'description': f'Description for test service {index}',
        'price': str(25 + index * 10),
        'duration': str(30 + index * 15),
    }


def generate_product_data(index=1):
    """Generate test product data."""
    return {
        'name': f'E2E Test Product {index}',
        'description': f'Description for test product {index}',
        'price': str(9.99 + index * 5),
        'quantity': str(50 + index * 10),
    }
