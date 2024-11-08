"""
gRPC server for handling client requests (from Flask App or other third-party applications) within Surf Shelter for the Features Processor Engine
"""

import grpc
from concurrent import futures
from . import features_pb2
from . import features_pb2_grpc
from .helpers import feature_extractor

class FeaturesProcessor(features_pb2_grpc.FeaturesProcessorServicer):

    def initialize_extractor(self, url, context):
        """Initialize the FeatureExtractor with error handling."""
        try:
            self.__extractor = feature_extractor.FeatureExtractor(url)
        except Exception as e:
            context.set_details(f"Error initializing FeatureExtractor: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return False
        return True

    def GenFeaturesUnusualExt(self, request, context):
        """
        gRPC endpoint that retrieves features related to unusual extension behavior for a given URL, 
        including metrics like URL length, TLD analysis score, IP address analysis score, and sub-domain analysis score.

        Returns a FeatureResponse if all features are retrieved successfully; otherwise, sets a FAILED_PRECONDITION error 
        if any feature is missing, or an INTERNAL error for unexpected issues.
        """
        if not self.initialize_extractor(request.url, context):
            return features_pb2.FeatureResponse()
        try:
            # Extract unusual extension features
            features = self.__extractor.get_unusual_ext_features()
            # Check if any feature is None, indicating an error in retrieval
            if any(value is None for value in features.values()):
                context.set_details("One or more unusual extension features could not be retrieved.")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return features_pb2.FeatureResponse()
            # If all features are valid, return them
            return features_pb2.FeatureResponse(features=features)
        except Exception as e:
            context.set_details(f"Error generating unusual extension features: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return features_pb2.FeatureResponse()

    def GenFeaturesTyposquatting(self, request, context):
        """
        gRPC endpoint that retrieves features related to typosquatting behavior for a given URL, specifically calculating 
        the Levenshtein distance to assess similarity to trusted domains.

        Returns a FeatureResponse with typosquatting-related features if successful; otherwise, sets a FAILED_PRECONDITION error 
        if any feature is missing, or an INTERNAL error for unexpected issues.
        """
        if not self.initialize_extractor(request.url, context):
            return features_pb2.FeatureResponse()
        try:
            # Extract typosquatting features
            features = self.__extractor.get_typosquatting_features()
            print(features)
            # Check if any feature is None, indicating an error in retrieval
            if any(value is None for value in features.values()):
                context.set_details("One or more typosquatting features could not be retrieved.")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return features_pb2.FeatureResponse()
            # If all features are valid, return them
            return features_pb2.FeatureResponse(features=features)
        except Exception as e:
            context.set_details(f"Error generating typosquatting features: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return features_pb2.FeatureResponse()

    def GenFeaturesPhishing(self, request, context):
        """
        gRPC endpoint that retrieves features related to phishing behavior for a given URL, including metrics such as 
        TTL, domain age, and reputation score.

        Returns a FeatureResponse with phishing-related features if successful; otherwise, sets a FAILED_PRECONDITION error 
        if any feature is missing, or an INTERNAL error for unexpected issues.
        """
        if not self.initialize_extractor(request.url, context):
            return features_pb2.FeatureResponse()
        try:
            # Extract phishing features
            features = self.__extractor.get_phishing_features()
            print(features)
            # Check if any feature is None, indicating an error in retrieval
            if any(value is None for value in features.values()):
                context.set_details("One or more phishing features could not be retrieved.")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return features_pb2.FeatureResponse()
            # If all features are valid, return them
            return features_pb2.FeatureResponse(features=features)
        except Exception as e:
            context.set_details(f"Error generating phishing features: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return features_pb2.FeatureResponse()


    def GenLabel(self, request, context):
        """
        gRPC endpoint that generates a prediction label indicating the likelihood of a URL being malicious, click fraud, or pay fraud.

        Returns a LabelResponse with the prediction results if successful; otherwise, sets an INTERNAL error if an unexpected issue occurs.
        """
        if not self.initialize_extractor(request.url, context):
            return features_pb2.LabelResponse()
        try:
            # Extract prediciton labels
            prediction = self.__extractor.get_prediction_label()
            # Check if any label is None, indicating an error in retrieval
            if any(value is None for value in prediction.values()):
                context.set_details("One or more prediction labels could not be retrieved.")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return features_pb2.LabelResponse()
            # If all features are valid, return them
            return features_pb2.LabelResponse(prediction=prediction)
        except Exception as e:
            context.set_details(f"Error generating prediction labels: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return features_pb2.LabelResponse()

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
