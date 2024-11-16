"""
gRPC client to handle Flask requests from Surf Shelter users for the Prediction Engine.
"""

import logging
import grpc
from google.protobuf.json_format import MessageToDict
from . import features_pb2
from . import features_pb2_grpc

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to create the gRPC stub
def get_grpc_stub():
    return grpc.insecure_channel("localhost:50051")

def get_prediction(url):
    try:
        with get_grpc_stub() as channel:
            stub = features_pb2_grpc.PredictionEngineStub(channel)
            raw_response = stub.MakePrediction(features_pb2.PredictionRequest(url=url))
            response = MessageToDict(
                raw_response,
                preserving_proto_field_name=True      # Use the proto field names as they are
            )
            # Handle missing "predicted_label" in prediction
            prediction_details = response.get("prediction_details", {})
            prediction = prediction_details.get("prediction", {})
            if "predicted_label" not in prediction:
                prediction["predicted_label"] = False
                prediction_details["prediction"] = prediction  # Update prediction
                response["prediction_details"] = prediction_details  # Ensure the updated details are saved
            return response
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e}")
        return {"error": "Failed to get prediction from gRPC server"}
