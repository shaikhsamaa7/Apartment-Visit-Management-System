"""
Apartment Visit Management System (AVMS) - Main Application Factory.
"""

import os
from flask import Flask, render_template
from config import config_by_name
from database.db import close_db, init_db
from security import (
    generate_csrf_token,
    validate_csrf_token,
    add_security_headers
)
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.visitor_routes import visitor_bp
from routes.pass_routes import pass_bp
from routes.category_routes import category_bp
from routes.report_routes import report_bp


def create_app(config_name=None):
    """Application factory for AVMS."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure the instance directory exists for sqlite database
    os.makedirs(app.instance_path, exist_ok=True)

    # Database connection teardown
    app.teardown_appcontext(close_db)

    # Security hooks
    app.before_request(validate_csrf_token)
    app.after_request(add_security_headers)

    # Template context processors
    @app.context_processor
    def inject_utilities():
        return {
            'csrf_token': generate_csrf_token(),
            'app_name': 'Apartment Visitor Management System'
        }

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(visitor_bp)
    app.register_blueprint(pass_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(report_bp)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    # Initialize schema and seed data
    init_db(app)

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
