"""
gRPC client to handle Flask requests from Surf Shelter users for the Prediction Engine.
"""

import requests
import logging
import grpc
from google.protobuf.json_format import MessageToDict
from . import features_pb2
from . import features_pb2_grpc
from . import feature_urls

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to create the gRPC stub
def get_grpc_stub():
    channel = grpc.insecure_channel("localhost:50051")
    return features_pb2_grpc.PredictionEngineStub(channel)


def get_prediction(url):
    try:
        # Payload for each feature request
        payload = {"url": url}
        # Get info for unusual extensions
        unusual_ext_response = requests.post(feature_urls.UNUSUAL_EXT_URL, json=payload)
        unusual_ext_response.raise_for_status()
        unusual_ext_info = unusual_ext_response.json()["features"]
        # Get info for typosquatting
        typosquatting_response = requests.post(
            feature_urls.TYPOSQUATTING_URL, json=payload
        )
        typosquatting_response.raise_for_status()
        typosquatting_info = typosquatting_response.json()["features"]
        # Get info for phishing
        phishing_response = requests.post(feature_urls.PHISHING_URL, json=payload)
        phishing_response.raise_for_status()
        phishing_info = phishing_response.json()["features"]
    except Exception as e:
        logger.error(f"Unexpected error occurred at Features Processor Engine: {e}")
        return {"error": "An unexpected error occurred"}

    try:
        stub = get_grpc_stub()
        prediction_request = {
            "unusualExtInfo": features_pb2.FeatureResponse(features=unusual_ext_info),
            "typosquattingInfo": features_pb2.FeatureResponse(
                features=typosquatting_info
            ),
            "phishingInfo": features_pb2.FeatureResponse(features=phishing_info),
        }
        prediction_response = MessageToDict(
            stub.MakePrediction(features_pb2.PredictionRequest(**prediction_request)),
        )
        # Handle when MessageToDict can't process false
        if "predictedLabel" not in prediction_response:
            prediction_response["predictedLabel"] = False
        # Log the response
        logger.info(f"Prediction result: {prediction_response}")
        return prediction_response
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e}")
        return {"error": "Failed to get prediction from gRPC server"}
