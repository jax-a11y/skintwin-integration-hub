"""
Test configuration and shared fixtures for all tests.
"""
import os
import sys
import pytest
from typing import Generator

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set CI-safe environment variables before importing app
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('FLASK_SECRET_KEY', 'test-secret-key-for-ci')
os.environ.setdefault('DATABASE_URL', 'sqlite:///test_salon.db')
os.environ.setdefault('TESTING', 'true')

# Disable external integrations
os.environ.setdefault('SHOPIFY_SHOP_NAME', '')
os.environ.setdefault('SHOPIFY_ACCESS_TOKEN', '')
os.environ.setdefault('WIX_API_KEY', '')
os.environ.setdefault('OPENCART_API_KEY', '')
os.environ.setdefault('STRIPE_SECRET_KEY', '')
os.environ.setdefault('PAYSTACK_SECRET_KEY', '')
os.environ.setdefault('OPENAI_API_KEY', '')


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    from flask import Flask
    from database import db_sql
    
    # Create a minimal test app
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.config['SECRET_KEY'] = 'test-secret'
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    test_app.config['WTF_CSRF_ENABLED'] = False
    test_app.config['LOGIN_DISABLED'] = False
    
    db_sql.init_app(test_app)
    
    with test_app.app_context():
        db_sql.create_all()
        yield test_app
        db_sql.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='session')
def db(app):
    """Get database instance."""
    from database import db_sql
    with app.app_context():
        yield db_sql


@pytest.fixture(scope='function')
def session(db, app):
    """Create a new database session for each test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        yield db.session
        
        transaction.rollback()
        connection.close()


@pytest.fixture
def admin_user(app, db):
    """Create an admin user for testing."""
    from database_models import User
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        user = User(
            username='TestAdmin',
            email='admin@test.com',
            password_hash=generate_password_hash('TestPassword123!'),
            is_admin=True,
            is_staff=True
        )
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def regular_user(app, db):
    """Create a regular user for testing."""
    from database_models import User
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        user = User(
            username='TestUser',
            email='user@test.com',
            password_hash=generate_password_hash('TestPassword123!'),
            is_admin=False,
            is_staff=False
        )
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def authenticated_client(client, admin_user, app):
    """Create an authenticated test client."""
    with app.app_context():
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user.id
            sess['_fresh'] = True
    return client


class FakeGateway:
    """Mock integration gateway for testing."""
    
    def __init__(self):
        self.connectors = {}
        self.initialized = True
    
    def health_check(self):
        return {
            "gateway": "healthy",
            "initialized": True,
            "connectors": {
                "shopify": {
                    "status": "connected",
                    "type": "ShopifyB2BConnector"
                },
                "wix": {
                    "status": "disconnected",
                    "type": "WixBookingsConnector"
                },
                "opencart": {
                    "status": "disconnected", 
                    "type": "OpenCartConnector"
                }
            }
        }
    
    def test_connections(self):
        return {
            "shopify": {"connected": True, "message": "Mock connection"},
            "wix": {"connected": False, "message": "Not configured"},
            "opencart": {"connected": False, "message": "Not configured"}
        }


@pytest.fixture
def fake_gateway():
    """Create a fake integration gateway."""
    return FakeGateway()


@pytest.fixture
def app_with_gateway(app, fake_gateway):
    """Create app with fake gateway registered."""
    app.extensions["integration_gateway"] = fake_gateway
    return app


# Playwright-specific fixtures for E2E tests
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests."""
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
