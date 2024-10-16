import threading
from grpc_service.grpc_server import serve as setup_grpc_server
from grpc_service.grpc_client import get_prediction

# Event to synchronize the start of the gRPC server and Flask server
grpc_ready_event = threading.Event()


# Helper to run the gRPC server in a separate thread
def start_grpc_server():
    setup_grpc_server()
    grpc_ready_event.set()  # Signal that the gRPC server is ready


if __name__ == "__main__":
    grpc_thread = threading.Thread(target=start_grpc_server)
    grpc_thread.daemon = True  # Set the gRPC server thread as a daemon
    grpc_thread.start()

    print("gRPC server is running as a daemon thread...")
    print(get_prediction("example.com"))

    # Run the Flask app in the main thread
