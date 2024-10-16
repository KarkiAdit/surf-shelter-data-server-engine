from flask import Blueprint, jsonify, abort
from app.utils import extract_and_validate_url
from grpc_service.grpc_client import get_prediction

feature_routes = Blueprint("feature_routes", __name__)


# Flask endpoint for features tied to unusual extensions behavior
@feature_routes.route("/prediction/predict", methods=["POST"])
def gen_features_unusual_ext():
    try:
        url = extract_and_validate_url()
        return jsonify(get_prediction(url))
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")
