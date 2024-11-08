from flask import Blueprint, jsonify, abort
from app.utils import extract_and_validate_url
from grpc_service.grpc_client import (
    get_features_unusual_ext,
    get_features_typosquatting,
    get_features_phishing,
    get_label_prediction,
)

feature_routes = Blueprint("feature_routes", __name__)


# Flask endpoint for features tied to unusual extensions behavior
@feature_routes.route("/features/unusual-extensions", methods=["POST"])
def gen_features_unusual_ext():
    try:
        url = extract_and_validate_url()
        return jsonify(get_features_unusual_ext(url))
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")


# Flask endpoint for features tied to typosquatted behavior
@feature_routes.route("/features/typosquatting", methods=["POST"])
def gen_features_typosquatting():
    try:
        url = extract_and_validate_url()
        return jsonify(get_features_typosquatting(url))
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")


# Flask endpoint for features tied to phishing behavior
@feature_routes.route("/features/phishing", methods=["POST"])
def gen_features_phishing():
    try:
        url = extract_and_validate_url()
        return jsonify(get_features_phishing(url))
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")


# Flask endpoint for generating the prediction label
@feature_routes.route("/features/label", methods=["POST"])
def generate_label():
    try:
        url = extract_and_validate_url()
        return jsonify(get_label_prediction(url))
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")
