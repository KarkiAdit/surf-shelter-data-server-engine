"""
gRPC server for handling client requests (from Flask App or other third-party applications) within Surf Shelter
"""

import grpc
from concurrent import futures
from . import features_pb2
from . import features_pb2_grpc


class FeaturesProcessor(features_pb2_grpc.FeaturesProcessorServicer):
    # gRPC endpoint for features tied to unusual extensions behavior
    def GenFeaturesUnusualExt(self, request, context):
        url = request.url
        # Add logic to fetch numerical values from public APIs for each feature
        features = {
            "url_length": float(35),
            "tld-analysis-score": float(90),
            "ip-address-analysis-score": float(90),
            "sub-domain-analysis-score": float(90),
        }
        return features_pb2.FeatureResponse(features=features)

    # gRPC endpoint for features tied to typosquatted behavior
    def GenFeaturesTyposquatting(self, request, context):
        url = request.url
        # Add logic to fetch numerical values from public APIs for each feature
        features = {
            "levenshtein_dx": float(5),
        }
        return features_pb2.FeatureResponse(features=features)

    # gRPC endpoint for features tied to phishing behavior
    def GenFeaturesPhishing(self, request, context):
        url = request.url
        # Add logic to fetch numerical values from public APIs for each feature
        features = {
            "time_to_live": float(15),
            "domain_age": float(7),
            "reputation_score": float(90),
        }
        return features_pb2.FeatureResponse(features=features)

    # gRPC endpoint for generating the prediction label
    def GenLabel(self, request, context):
        url = request.url
        # Add logic to make the prediction
        prediction = {
            "is_malicious": False,
            "is_click_fraud": False,
            "is_pay_fraud": False,
        }
        return features_pb2.LabelResponse(prediction=prediction)


def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    features_pb2_grpc.add_FeaturesProcessorServicer_to_server(
        FeaturesProcessor(), server
    )
    server.add_insecure_port("[::]:50051")
    # Start the server
    server.start()
    print("gRPC server is running on port 50051...")
    # Keep the server running
    server.wait_for_termination()
