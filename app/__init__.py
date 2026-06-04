"""
Flask Application Factory

This module implements the Flask app factory pattern for creating
application instances with proper configuration and blueprint registration.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_cors import CORS


def create_app(config_name='development'):
    """
    Create and configure the Flask application.
    
    Args:
        config_name (str): Configuration environment ('development', 'testing', 'production')
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config
    app.config.from_object(config.get(config_name, config['development']))
    
    # Enable CORS
    CORS(app)
    
    # Configure logging
    _configure_logging(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    app.logger.info(f'Flask application created in {config_name} mode')
    
    return app


def _configure_logging(app):
    """
    Configure application logging with rotating file handler.
    
    Args:
        app (Flask): Flask application instance
    """
    if not app.debug:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Set up rotating file handler
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        # Set log format
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        
        # Set log level
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        file_handler.setLevel(getattr(logging, log_level))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, log_level))
        app.logger.info('Flask application startup')


def _register_blueprints(app):
    """
    Register application blueprints.
    
    Args:
        app (Flask): Flask application instance
    """
    from app.routes.dashboard import dashboard_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)


def _register_error_handlers(app):
    """
    Register global error handlers.
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        app.logger.warning(f'404 error: {error}')
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        app.logger.error(f'500 error: {error}')
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors."""
        app.logger.warning(f'400 error: {error}')
        return {'error': 'Bad request'}, 400
