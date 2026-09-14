import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify

from app.config import config
from app.extensions import db, migrate, cors

load_dotenv()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    configure_logging(app)
    configure_extensions(app)
    configure_error_handlers(app)
    register_blueprints(app)

    return app


def configure_logging(app):
    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format=app.config["LOG_FORMAT"],
    )
    app.logger.setLevel(app.config["LOG_LEVEL"])


def configure_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)

    raw_origins = os.environ.get('CORS_ORIGINS', '')
    origins = [o.strip() for o in raw_origins.split(',') if o.strip()] or ['http://localhost:3001']
    cors.init_app(app, resources={r"/*": {"origins": origins}})


def configure_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": str(error)}), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal error: {error}")
        return jsonify({"error": "An unexpected error occurred"}), 500


def register_blueprints(app):
    from app.controllers.auth_controller import auth_bp
    from app.controllers.account_controller import account_bp
    from app.controllers.transaction_controller import transaction_bp
    from app.controllers.contact_controller import contact_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(account_bp, url_prefix="/accounts")
    app.register_blueprint(transaction_bp, url_prefix="/transactions")
    app.register_blueprint(contact_bp, url_prefix="/contacts")
