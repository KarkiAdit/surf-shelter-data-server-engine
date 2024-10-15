"""
gRPC client to handle Flask requests from Surf Shelter users for the Features Processor Engine.
"""

from google.protobuf.json_format import MessageToDict
import grpc
from . import features_pb2
from . import features_pb2_grpc


# Function to create the gRPC stub
def get_grpc_stub():
    channel = grpc.insecure_channel("localhost:50051")
    return features_pb2_grpc.FeaturesProcessorStub(channel)


def get_features_unusual_ext(url):
    stub = get_grpc_stub()
    response = MessageToDict(
        stub.GenFeaturesUnusualExt(features_pb2.FeatureRequest(url=url))
    )
    return response


def get_features_typosquatting(url):
    stub = get_grpc_stub()
    response = MessageToDict(
        stub.GenFeaturesTyposquatting(features_pb2.FeatureRequest(url=url))
    )
    return response


def get_features_phishing(url):
    stub = get_grpc_stub()
    response = MessageToDict(
        stub.GenFeaturesPhishing(features_pb2.FeatureRequest(url=url))
    )
    return response


def get_label_prediction(url):
    stub = get_grpc_stub()
    label_response = MessageToDict(stub.GenLabel(features_pb2.FeatureRequest(url=url)))
    return label_response
