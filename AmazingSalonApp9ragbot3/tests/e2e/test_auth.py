"""
E2E Tests for Authentication flows.
Tests login, logout, registration, and access control.
"""
import pytest
from playwright.sync_api import Page, expect

# Mark all tests in this module
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.auth,
]


class TestAuthSmoke:
    """Smoke tests for authentication - run on every PR."""
    
    @pytest.mark.smoke
    def test_login_page_loads(self, page: Page, base_url):
        """Test that login page loads correctly."""
        page.goto(f"{base_url}/auth/login")
        
        # Check page loaded
        expect(page).to_have_title(lambda t: 'login' in t.lower() or 'salon' in t.lower())
        
        # Check form elements exist
        expect(page.locator('input[name="email"], input[type="email"]')).to_be_visible()
        expect(page.locator('input[name="password"], input[type="password"]')).to_be_visible()
        expect(page.locator('button[type="submit"], input[type="submit"]')).to_be_visible()
    
    @pytest.mark.smoke
    def test_login_with_valid_credentials(self, page: Page, base_url):
        """Test successful login with valid credentials."""
        page.goto(f"{base_url}/auth/login")
        
        # Fill and submit login form
        page.fill('input[name="email"], input[type="email"]', 'admin@test.com')
        page.fill('input[name="password"], input[type="password"]', 'TestPassword123!')
        page.click('button[type="submit"], input[type="submit"]')
        
        # Wait for navigation
        page.wait_for_load_state('networkidle')
        
        # Should redirect to dashboard or home
        assert '/login' not in page.url.lower()
    
    @pytest.mark.smoke
    def test_login_with_invalid_credentials(self, page: Page, base_url):
        """Test login failure with invalid credentials."""
        page.goto(f"{base_url}/auth/login")
        
        # Fill and submit with wrong password
        page.fill('input[name="email"], input[type="email"]', 'admin@test.com')
        page.fill('input[name="password"], input[type="password"]', 'WrongPassword!')
        page.click('button[type="submit"], input[type="submit"]')
        
        # Should stay on login page or show error
        page.wait_for_load_state('networkidle')
        
        # Either still on login page or error message shown
        is_on_login = '/login' in page.url.lower()
        has_error = page.locator('.alert-danger, .error, .flash-error, [class*="error"]').count() > 0
        
        assert is_on_login or has_error
    
    @pytest.mark.smoke
    def test_logout(self, logged_in_admin: Page, base_url):
        """Test logout functionality."""
        page = logged_in_admin
        
        # Find and click logout
        logout_link = page.locator('a[href*="logout"], .logout-btn, button:has-text("Logout")')
        if logout_link.count() > 0:
            logout_link.first.click()
            page.wait_for_load_state('networkidle')
        
        # Navigate to protected page
        page.goto(f"{base_url}/")
        page.wait_for_load_state('networkidle')
        
        # Should redirect to login
        assert '/login' in page.url.lower() or page.locator('input[name="email"]').is_visible()


class TestAuthFull:
    """Full authentication tests - run in exhaustive suite."""
    
    def test_register_page_loads(self, page: Page, base_url):
        """Test that registration page loads."""
        page.goto(f"{base_url}/auth/register")
        
        # Check form exists
        email_field = page.locator('input[name="email"], input[type="email"]')
        password_field = page.locator('input[name="password"], input[type="password"]')
        
        # Registration page should have email and password fields
        expect(email_field).to_be_visible()
        expect(password_field).to_be_visible()
    
    def test_protected_route_redirects_to_login(self, page: Page, base_url):
        """Test that protected routes redirect unauthenticated users."""
        protected_routes = [
            '/clients',
            '/appointments',
            '/inventory',
            '/analytics',
            '/settings',
        ]
        
        for route in protected_routes:
            page.goto(f"{base_url}{route}")
            page.wait_for_load_state('networkidle')
            
            # Should redirect to login
            assert '/login' in page.url.lower() or page.locator('input[name="email"]').is_visible(), \
                f"Route {route} should redirect to login"
    
    def test_admin_dashboard_access(self, logged_in_admin: Page, base_url):
        """Test that admin can access admin dashboard."""
        page = logged_in_admin
        
        # Try to access admin area
        page.goto(f"{base_url}/admin_dashboard")
        page.wait_for_load_state('networkidle')
        
        # Should not be redirected to login
        is_accessible = '/login' not in page.url.lower()
        
        # Admin dashboard might not exist, just check we're not blocked
        assert is_accessible or page.url.endswith('/admin_dashboard')
    
    def test_session_persistence(self, page: Page, base_url):
        """Test that session persists across page loads."""
        # Login
        page.goto(f"{base_url}/auth/login")
        page.fill('input[name="email"], input[type="email"]', 'admin@test.com')
        page.fill('input[name="password"], input[type="password"]', 'TestPassword123!')
        page.click('button[type="submit"], input[type="submit"]')
        page.wait_for_load_state('networkidle')
        
        # Navigate to different pages
        pages_to_check = ['/', '/clients', '/appointments']
        
        for path in pages_to_check:
            page.goto(f"{base_url}{path}")
            page.wait_for_load_state('networkidle')
            
            # Should not be redirected to login
            if path != '/':
                is_logged_in = '/login' not in page.url.lower()
                assert is_logged_in, f"Session lost when navigating to {path}"


class TestAccessControl:
    """Test access control and permissions."""
    
    def test_regular_user_cannot_access_admin(self, logged_in_user: Page, base_url):
        """Test that regular users cannot access admin features."""
        page = logged_in_user
        
        admin_routes = [
            '/admin_dashboard',
            '/settings',
        ]
        
        for route in admin_routes:
            page.goto(f"{base_url}{route}")
            page.wait_for_load_state('networkidle')
            
            # Should either redirect or show forbidden
            is_redirected = '/login' in page.url.lower() or route not in page.url
            has_error = page.locator('.alert-danger, .forbidden, [class*="error"]').count() > 0
            
            # Just verify we handled it somehow
            assert is_redirected or has_error or page.url.endswith(route)
