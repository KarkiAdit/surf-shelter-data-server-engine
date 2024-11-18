"""
gRPC server for handling client requests (from Flask App or other third-party applications) within Surf Shelter for the Prediction Engine.
"""

import os
import requests
import grpc
import logging
import joblib
import io
import pandas as pd
from concurrent import futures
from pymongo import MongoClient
from google.cloud import storage
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
        self.__collection = self.__db["predicted_urls_records"]
        # Load the recent GCS model
        self.__load_model_from_gcs("surf-shelter-model-v0", "models/svm_model_v0.pkl")
        # Set common info for Feature Processor requests
        self.__BASE_URL = os.getenv('FEATURE_PROCESSOR_SERVICE_URL')
        self.__headers = {
            "Content-Type": "application/json"
        }

    def __load_model_from_gcs(self, bucket_name, model_file_path):
        """Load the trained SVM model from GCS."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(model_file_path)
        model_data = blob.download_as_bytes()
        self.__model = joblib.load(io.BytesIO(model_data))

    def __fetch_feature_values(self):
        """
        Fetches feature values for a given URL by querying multiple API endpoints from the Features Processor Engine. 
        Updates the input_data DataFrame with the fetched values if all endpoints succeed; sets it to None if any endpoint fails. 
        Raises an error if the base URL for the Features Processor Engine is not configured.
        """
        if self.__BASE_URL is None:
            raise ValueError("FEATURE_PROCESSOR_SERVICE_URL environment variable is not set.")
        data = {
            "url": self.__url
        }
        # Helper function to send a POST request to the Features Processor Engine and update input_data
        def fetch_and_update(endpoint: str, attributes: set, non_match: dict = None) -> bool:
            try:
                response = requests.post(f"{self.__BASE_URL}/{endpoint}", json=data, headers=self.__headers)
                response.raise_for_status()
                response_data = response.json()["features"]
                # Update curr_row with non-matching keys if non_match is provided
                if non_match:
                    for key, value_key in non_match.items():
                        self.__input_data[key] = response_data.get(value_key, self.__input_data[key])
                        attributes.remove(key)
                # Update curr_row with attributes that match response_data directly
                for attribute in attributes:
                    self.__input_data[attribute] = response_data.get(attribute, self.__input_data[attribute])
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
        ): 
            self.__input_data = None
            return

        # Fetch and update feature values for each typosquatting attribute
        if not fetch_and_update(
            "typosquatting", 
            {'levenshtein_dx'}
        ): 
            self.__input_data = None
            return

        # Fetch and update feature values for each phishing attribute
        if not fetch_and_update(
            "phishing", 
            {'time_to_live', 'domain_age', 
            #  'reputation_score' Avoid reputation score for testing purposes
             }
        ): 
            self.__input_data = None
            return

    def __fetch_y_true(self):
        """Fetches the true label (y_test) for a given URL from an external API."""
        try:
            data = {"url": self.__url}
            response = requests.post(f"{self.__BASE_URL}/label", json=data, headers=self.__headers)
            response.raise_for_status()
            # Retrieve the 'is_malicious' value and convert it to an integer (0 or 1)
            self.__y_true = int(response.json()["prediction"].get("is_malicious", 0))
        except requests.exceptions.RequestException as e:
            print("Error fetching label feature values:", e)
            # Default to a non-malicious label (False) if there's an error
            self.__y_true = 0

    def MakePrediction(self, request, context):
        """
        Handles prediction requests by checking for an existing prediction in the database or, if absent, 
        fetching feature values, making a new prediction using the trained SVM model, and storing the result. 
        Returns a PredictionResponse with the predicted label, accuracy, p-value accuracy, and loss. 
        In case of errors, returns a default prediction with pre-defined values.
        """
        self.__url = request.url
        # Check if the url has already been predicted before
        existing_record = self.__collection.find_one({"url": self.__url})
        if existing_record:
            # If found, return the existing prediction
            response = features_pb2.PredictionResponse(
                status=features_pb2.ResponseStatus(
                    code=200,
                    message="Prediction found in existing records"
                ),
                prediction_details=features_pb2.PredictionDetails(
                    features=features_pb2.Features(
                        **existing_record['prediction_details']['features']
                    ),
                    prediction=features_pb2.Prediction(
                        **existing_record['prediction_details']['prediction']
                    )
                )
            )
            return response
        # If no existing record, fetch feature values, make a new prediction, and update the New Rows Database
        self.__input_data = {
            'url_length': 0.0,
            'tld_analysis_score': 0.0,
            'ip_analysis_score': 0.0,
            'sub_domain_analysis_score': 0.0,
            'levenshtein_dx': 0.0,
            'time_to_live': 0.0,
            'domain_age': 0.0,
            'reputation_score': 0.0
        }
        # Fetch feature values
        self.__fetch_feature_values()
        if self.__input_data:
            logger.info(f"Features info: {self.__input_data}")
            # Use the SVM trained model to make a prediction
            feature_names = self.__model.feature_names_in_
            feature_values = pd.DataFrame([self.__input_data], columns=feature_names)
            models_prediction = self.__model.predict(feature_values)
            predicted_label = models_prediction[0]
            # Evaluate the true label for accuracy calculation
            self.__fetch_y_true()
            # Calculate accuracy for the model
            accuracy = int(self.__y_true == predicted_label)
            TP = int(self.__y_true == 1 and predicted_label == 1)
            FP = int(self.__y_true == 0 and predicted_label == 1)
            # Calculate precision for the model
            precision = 1.0 if TP + FP == 0 else TP / (TP + FP)
            # Create prediction details
            prediction = {
                "predicted_label": bool(predicted_label),
                "accuracy": float(accuracy),
                "precision": float(precision),
                "loss": -1.0  # Default value for loss
            }
            prediction_details = {
                "features": self.__input_data,
                "prediction": prediction
            }
            # Update New Sampled Rows table
            db_entry = {
                "url": self.__url,
                "prediction_details": prediction_details
            }
            self.__collection.insert_one(db_entry)
            # Return the new prediction
            return features_pb2.PredictionResponse(
                status=features_pb2.ResponseStatus(
                    code=200,
                    message="Prediction made using ML trained model on the GCS."
                ),
                prediction_details=features_pb2.PredictionDetails(
                    features=features_pb2.Features(**self.__input_data),
                    prediction=features_pb2.Prediction(**prediction)
                )
            )
        # Return a response indicating a server-side error
        return features_pb2.PredictionResponse(
            status=features_pb2.ResponseStatus(
                code=500,
                message="Prediction failed due to a server-side error. A feature could not be processed."
            )
        )

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    features_pb2_grpc.add_PredictionEngineServicer_to_server(
        PredictionProcessor(), server
    )
    server.add_insecure_port("0.0.0.0:50051")
    # Start the server
    server.start()
    print("gRPC server is running on port 50051...")
    # Keep the server running
    server.wait_for_termination()
