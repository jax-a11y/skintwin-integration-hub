from flask import Blueprint, current_app, render_template, request
from flask_login import login_required

bp = Blueprint('integrations_hub', __name__)


def _gateway_status():
    gateway = current_app.extensions.get("integration_gateway")
    if not gateway:
        return {
            "gateway": "unavailable",
            "initialized": False,
            "connectors": {}
        }

    try:
        return gateway.health_check()
    except Exception as e:
        return {
            "gateway": "error",
            "initialized": False,
            "connectors": {},
            "error": str(e)
        }


@bp.route('/integrations/hub')
@login_required
def hub():
    status = _gateway_status()
    return render_template(
        'shopify_app_hub.html',
        status=status,
        shop_domain=request.args.get('shop', ''),
        embedded=False
    )


@bp.route('/shopify/app')
def shopify_app():
    status = _gateway_status()
    return render_template(
        'shopify_app_hub.html',
        status=status,
        shop_domain=request.args.get('shop', ''),
        embedded=True
    )
