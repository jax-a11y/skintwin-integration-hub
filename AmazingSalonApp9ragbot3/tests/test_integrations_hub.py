import os
import unittest
import importlib.util
from flask import Flask

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ROUTE_FILE = os.path.join(BASE_DIR, "routes", "integrations_hub.py")
SPEC = importlib.util.spec_from_file_location("integrations_hub_route", ROUTE_FILE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
bp = MODULE.bp


class FakeGateway:
    def health_check(self):
        return {
            "gateway": "healthy",
            "initialized": True,
            "connectors": {
                "shopify": {
                    "status": "connected",
                    "type": "ShopifyB2BConnector"
                }
            }
        }


class ShopifyHubRouteTests(unittest.TestCase):
    def setUp(self):
        template_dir = os.path.join(BASE_DIR, "templates")
        self.app = Flask(__name__, template_folder=template_dir)
        self.app.config["TESTING"] = True
        self.app.secret_key = "test-secret"
        self.app.register_blueprint(bp)
        self.app.extensions["integration_gateway"] = FakeGateway()
        self.client = self.app.test_client()

    def test_shopify_app_page_renders_shop_context_and_connector(self):
        response = self.client.get("/shopify/app?shop=test-shop.myshopify.com")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Shopify App Connector Hub", body)
        self.assertIn("test-shop.myshopify.com", body)
        self.assertIn("ShopifyB2BConnector", body)


if __name__ == "__main__":
    unittest.main()
