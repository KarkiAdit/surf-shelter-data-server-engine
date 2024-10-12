import threading
from app import create_app
from grpc_service.grpc_server import serve as setup_grpc_server

# Event to synchronize the start of the gRPC server and Flask server
grpc_ready_event = threading.Event()


# Helper to run the Flask app in a separate thread
def start_flask_app():
    app = create_app()
    app.run(host="0.0.0.0", port=5001)


# Helper to run the gRPC server in a separate thread
def start_grpc_server():
    setup_grpc_server()
    grpc_ready_event.set()  # Signal that the gRPC server is ready


if __name__ == "__main__":
    grpc_thread = threading.Thread(target=start_grpc_server)
    grpc_thread.daemon = True  # Set the gRPC server thread as a daemon
    grpc_thread.start()

    print("gRPC server is running as a daemon thread...")

    # Run the Flask app in the main thread
    start_flask_app()
    print(
        "Flask server has stopped running. Daemon thread for gRPC server will terminate automatically."
    )
    print("Both gRPC server and Flask server have stopped running.")
