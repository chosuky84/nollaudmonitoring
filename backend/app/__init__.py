# backend/app/__init__.py

from flask import Flask

def create_app():
    app = Flask(__name__)

    from .resources import oracle_monitoring
    app.register_blueprint(oracle_monitoring.bp)

    @app.route('/')
    def home():
        return 'Hello, Oracle Cloud!'

    return app
