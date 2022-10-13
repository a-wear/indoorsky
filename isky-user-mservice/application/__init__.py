# application/__init__.py
from config import app_config
import os
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_cors import CORS
from .presentation import app
from .presentation.data_injection.injection_container import ApplicationContainer
cors = CORS()
bcrypt = Bcrypt()

def init_jwt(app):
    from application.core.decorators.jwt_manager import jwt_manager
    jwt_manager.init_app(app)
    
def create_app(config_name):
    container = ApplicationContainer()
    container.wire(modules=[__name__])
    
    with app.app_context():
        # Register blueprints
        from .presentation.endpoints.user_endpoints import api_user
        app.config.from_object(app_config[config_name])
        app.register_api(api_user)
        cors.init_app(app)
        bcrypt.init_app(app)
        init_jwt(app=app)
        return app