"""
Gateway to the Flask server for the Prediction Engine
From a given URL, this microservice will return a predicted label using the most recent ML model to make a prediction
"""

from flask import Flask
from app.routes import feature_routes


def create_app():
    app = Flask(__name__)
    app.register_blueprint(feature_routes)
    return app
