"""
gRPC server for handling client requests (from Flask App or other third-party applications) within Surf Shelter for the Prediction Engine.
"""

import os
import requests
import grpc
import logging
from typing import Optional
import time
from concurrent import futures
from pymongo import MongoClient
from . import features_pb2
from . import features_pb2_grpc

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionProcessor(features_pb2_grpc.PredictionEngineServicer):

    def __init__(self):
        # Configure MongoDB client with the correct database and collection
        self.__client = MongoClient(os.getenv("MONGODB_CONFIG_STR"))
        self.__db = self.__client["new_sampled_rows"]
        self.__collection = self.__db["predicted_urls_info"]

    def fetch_feature_values(self, url) -> Optional[dict]:
        """Fetch feature values for a given URL from different API endpoints provided by the Features Processor Engine.
        
        Returns:
            A dictionary containing feature values if all API endpoints succeed; otherwise, returns None if any endpoint fails.
        """
        BASE_URL = os.getenv('FEATURE_PROCESSOR_SERVICE_URL')
        if BASE_URL is None:
            raise ValueError("FEATURE_PROCESSOR_SERVICE_URL environment variable is not set.")
        data = {
            "url": url
        }
        headers = {
            "Content-Type": "application/json"
        }
        # Initialize curr_row with default values
        curr_row = {
            'url_length': 0.0,
            'tld_analysis_score': 0.0,
            'ip_analysis_score': 0.0,
            'sub_domain_analysis_score': 0.0,
            'levenshtein_dx': 0.0,
            'time_to_live': 0.0,
            'domain_age': 0.0,
            'reputation_score': 0.0,
        }
        # Helper function to send a POST request to the Features Processor Engine and update curr_row
        def fetch_and_update(endpoint: str, attributes: set, non_match: dict = None) -> bool:
            try:
                response = requests.post(f"{BASE_URL}/{endpoint}", json=data, headers=headers)
                if endpoint == "phishing":
                    time.sleep(7)
                response.raise_for_status()
                response_data = response.json()
                # Update curr_row with non-matching keys if non_match is provided
                if non_match:
                    for key, value_key in non_match.items():
                        curr_row[key] = response_data.get(value_key, curr_row[key])
                        attributes.discard(key)
                # Update curr_row with attributes that match response_data directly
                for attribute in attributes:
                    curr_row[attribute] = response_data.get(attribute, curr_row[attribute])
                return True
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {endpoint} feature values:", e)
                return False

        # Fetch and update feature values for each unusual extensions' attribute
        if not fetch_and_update(
            "unusual-extensions", 
            {'url_length', 'tld_analysis_score', 'ip_analysis_score', 'sub_domain_analysis_score'}, 
            {
                'tld_analysis_score': 'tld-analysis-score', 
                'ip_analysis_score': 'ip-analysis-score', 
                'sub_domain_analysis_score': 'sub-domain-analysis-score'
            }
        ): return None

        # Fetch and update feature values for each typosquatting attribute
        if not fetch_and_update(
            "typosquatting", 
            {'levenshtein_dx'}
        ): return None

        # Fetch and update feature values for each phishing attribute
        if not fetch_and_update(
            "phishing", 
            {'time_to_live', 'domain_age', 'reputation_score'}
        ): return None

        # Return the fetched feature values
        return curr_row

    # gRPC endpoint for making the prediction
    def MakePrediction(self, request, context):
        url = request.url
        # Check if the url has already been predicted before
        existing_record = self.__collection.find_one({"url": url})
        if existing_record:
            # If found, return the existing prediction
            prediction = {
                "predictedLabel": existing_record["predictedLabel"],
                "accuracy": existing_record["accuracy"],
                "pValueAccuracy": existing_record["pValueAccuracy"],
                "loss": existing_record["loss"],
            }
            return features_pb2.PredictionResponse(**prediction)
        
        # If no existing record, fetch feature values and make a new prediction
        curr_url_row = self.fetch_feature_values(request.url)
        if curr_url_row:
            logger.info(f"Unusual Extension Info: {curr_url_row}")
            # Use trained model from GCS bucket to make a prediction
            # Update New Sampled Rows table
        prediction = {
            "predictedLabel": False,
            "accuracy": 0.95,
            "pValueAccuracy": 0.05,
            "loss": 0.15,
        }
        # default value
        return features_pb2.PredictionResponse(**prediction)


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
