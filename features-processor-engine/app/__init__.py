"""
Gateway to the Flask server for the Features Processor Engine
From a given URL, this microservice will generate numerical values for all features selected to build our ML model and their associated label.
"""

from flask import Flask
from app.routes import feature_routes


def create_app():
    app = Flask(__name__)
    app.register_blueprint(feature_routes)
    return app
