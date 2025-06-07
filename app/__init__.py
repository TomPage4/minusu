from flask import Flask, request
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from .config import Config
from .utils.security import block_large_requests, apply_security_headers

# Initialize extensions without an app
mail = Mail()
limiter = Limiter(key_func=get_remote_address)

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """
    Application factory: creates and configures the Flask app.
    Useful for multiple environments & testing.
    """
    app = Flask(__name__)
    # Load configuration from Config class
    app.config.from_object(Config)

    # Initialize extensions with the app
    mail.init_app(app)
    limiter.init_app(app)

    # Register middleware
    app.before_request(block_large_requests)
    app.after_request(apply_security_headers)

    # Import and register blueprints
    from .routes.main import main_bp
    from .routes.contact import contact_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)

    try:
        from .ecommerce import ecommerce_bp
        app.register_blueprint(ecommerce_bp)
    except ImportError:
        pass

    @app.context_processor
    def inject_snipcart_globals():
        return {
            "snipcart_api_key": app.config.get("SNIPCART_API_KEY", "")
        }
    
    try:
        from .booking import booking_bp
        app.register_blueprint(booking_bp)
    except ImportError:
        pass

    from .admin import cms_bp
    app.register_blueprint(cms_bp)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'

    from app.admin.auth import admin_bp
    app.register_blueprint(admin_bp)

    return app