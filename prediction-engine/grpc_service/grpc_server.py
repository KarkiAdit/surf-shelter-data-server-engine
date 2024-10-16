"""
gRPC server for handling client requests (from Flask App or other third-party applications) within Surf Shelter for the Prediction Engine.
"""

import grpc
import logging
from concurrent import futures
from . import features_pb2
from . import features_pb2_grpc

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionProcessor(features_pb2_grpc.PredictionEngineServicer):
    # gRPC endpoint for making the prediction
    def MakePrediction(self, request, context):
        # Access the feature information from the request
        unusual_ext_info = request.unusualExtInfo.features
        typosquatting_info = request.typosquattingInfo.features
        phishing_info = request.phishingInfo.features

        logger.info(f"Unusual Extension Info: {unusual_ext_info}")
        logger.info(f"Typosquatting Info: {typosquatting_info}")
        logger.info(f"Phishing Info: {phishing_info}")

        # Use recent model from Recent Models table to make a prediction
        # Update New Sampled Rows table
        predictionLabel = False  # default value
        return features_pb2.PredictionResponse(predictedLabel=predictionLabel)


def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    features_pb2_grpc.add_PredictionEngineServicer_to_server(
        PredictionProcessor(), server
    )
    server.add_insecure_port("[::]:50051")
    # Start the server
    server.start()
    print("gRPC server is running on port 50051...")
    # Keep the server running
    server.wait_for_termination()
