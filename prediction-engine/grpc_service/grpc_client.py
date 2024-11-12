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
    channel = grpc.insecure_channel("localhost:50051")
    return features_pb2_grpc.PredictionEngineStub(channel)


def get_prediction(url):
    try:
        stub = get_grpc_stub()
        response = MessageToDict(
            stub.MakePrediction(features_pb2.PredictionRequest(url=url))
        )
        return response
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e}")
        return {"error": "Failed to get prediction from gRPC server"}
