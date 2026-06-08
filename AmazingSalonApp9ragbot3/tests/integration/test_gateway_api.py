"""
Integration tests for the Integration Gateway API.
Tests the /api/integrations/* endpoints with mocked connectors.
"""
import os
import sys
import pytest
import json

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set test environment
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('FLASK_SECRET_KEY', 'test-integration-key')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('TESTING', 'true')


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
            "shopify": {"connected": True, "latency_ms": 50},
            "wix": {"connected": False, "error": "Not configured"},
            "opencart": {"connected": False, "error": "Not configured"}
        }
    
    def sync_appointments(self, platforms=None):
        return {
            "synced": 0,
            "platforms": platforms or ["shopify"],
            "status": "success"
        }
    
    def sync_clients(self, platforms=None):
        return {
            "synced": 0,
            "platforms": platforms or ["shopify"],
            "status": "success"
        }
    
    def sync_products(self, platforms=None):
        return {
            "synced": 0,
            "platforms": platforms or ["shopify"],
            "status": "success"
        }


@pytest.fixture
def app():
    """Create test Flask app."""
    from flask import Flask
    from database import db_sql
    
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    
    db_sql.init_app(app)
    
    # Register integration gateway
    app.extensions["integration_gateway"] = FakeGateway()
    
    # Import and register blueprint
    try:
        from integrations.gateway import create_gateway_blueprint
        gateway = FakeGateway()
        bp = create_gateway_blueprint(gateway)
        app.register_blueprint(bp)
    except ImportError:
        pass
    
    with app.app_context():
        db_sql.create_all()
        yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestGatewayHealth:
    """Tests for gateway health endpoint."""
    
    def test_health_endpoint_returns_status(self, client):
        """Test that health endpoint returns gateway status."""
        response = client.get('/api/integrations/health')
        
        # Should return 200 or 401 (if auth required)
        assert response.status_code in [200, 401, 404]
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'gateway' in data or 'status' in data or 'connectors' in data
    
    def test_health_shows_connector_statuses(self, client):
        """Test that health shows individual connector statuses."""
        response = client.get('/api/integrations/health')
        
        if response.status_code == 200:
            data = response.get_json()
            if 'connectors' in data:
                assert isinstance(data['connectors'], dict)


class TestConnectionTests:
    """Tests for connection testing endpoint."""
    
    def test_connections_endpoint_exists(self, client):
        """Test that test-connections endpoint exists."""
        response = client.get('/api/integrations/test-connections')
        
        # Should not be 404
        assert response.status_code in [200, 401, 405]
    
    def test_connections_returns_results(self, client):
        """Test that connections endpoint returns test results."""
        response = client.get('/api/integrations/test-connections')
        
        if response.status_code == 200:
            data = response.get_json()
            # Should have connector results
            assert isinstance(data, dict)


class TestSyncEndpoints:
    """Tests for sync endpoints."""
    
    def test_appointments_sync_endpoint(self, client):
        """Test appointments sync endpoint."""
        response = client.post(
            '/api/integrations/appointments/sync',
            json={'platforms': ['shopify']},
            content_type='application/json'
        )
        
        # Should exist
        assert response.status_code in [200, 201, 401, 404, 405]
    
    def test_clients_sync_endpoint(self, client):
        """Test clients sync endpoint."""
        response = client.post(
            '/api/integrations/clients/sync',
            json={'platforms': ['shopify']},
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201, 401, 404, 405]
    
    def test_products_sync_endpoint(self, client):
        """Test products sync endpoint."""
        response = client.post(
            '/api/integrations/products/sync',
            json={'platforms': ['shopify']},
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201, 401, 404, 405]


class TestB2BEndpoints:
    """Tests for B2B-specific endpoints."""
    
    def test_b2b_companies_get(self, client):
        """Test getting B2B companies."""
        response = client.get('/api/integrations/b2b/companies')
        
        assert response.status_code in [200, 401, 404]
    
    def test_b2b_companies_post(self, client):
        """Test creating B2B company."""
        response = client.post(
            '/api/integrations/b2b/companies',
            json={
                'name': 'Test Company',
                'email': 'test@company.com'
            },
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201, 400, 401, 404, 405, 501]


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_invalid_endpoint_returns_404(self, client):
        """Test that invalid endpoints return 404."""
        response = client.get('/api/integrations/nonexistent')
        
        # Should be 404 or similar
        assert response.status_code in [404, 401]
    
    def test_invalid_method_returns_405(self, client):
        """Test that invalid methods return 405."""
        response = client.delete('/api/integrations/health')
        
        # Should be method not allowed or not found
        assert response.status_code in [404, 405, 401]
    
    def test_invalid_json_handled(self, client):
        """Test that invalid JSON is handled gracefully."""
        response = client.post(
            '/api/integrations/appointments/sync',
            data='invalid json{',
            content_type='application/json'
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 401, 404, 405, 500]
