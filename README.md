# 🚀 Data Server Engine

The **Data Server Engine** is a middleware component designed to facilitate communication between the **Frontend Client** and the **Model Processor**. It is built as a Flask API service, capable of handling gRPC requests, and consists of two main microservices:

- 📊 **Features Processor Engine**
- 🔮 **Prediction Engine**

This project is designed to be scalable, modular, and cloud-ready, hosted on **Google Cloud Run** using Dockerized images for each microservice.

## 📁 Project Structure

```
.
/data-server-engine
    /features-processor-engine
        ├── app/
            ├── __init__.py
            ├── routes.py
            ├── utils.py
        ├── grpc/
            ├── features.proto
            ├── features_pb2.py
            ├── features_pb2_grpc.py
            ├── grpc_server.py
            ├── grpc_client.py
        ├── Dockerfile
        ├── requirements.txt
        └── main.py
    /prediction-engine
        ├── app/
            ├── __init__.py
            ├── routes.py
            ├── utils.py
        ├── grpc/
            ├── features.proto
            ├── features_pb2.py
            ├── features_pb2_grpc.py
            ├── grpc_server.py
            ├── grpc_client.py
        ├── Dockerfile
        ├── requirements.txt
        └── main.py
    ├── docker-compose.yml
    └── README.md
```

## 📊 Features Processor Engine

The **Features Processor Engine** is a Flask microservice responsible for generating numerical values for each feature that will be used to build the ML model. Here's what it does:

- Generates feature values from URLs using publicly available APIs or custom functions based on research.
- Provides API endpoints for each selected feature as well as an endpoint for generating labels.
- Acts as a crucial component for constructing the training set.

### 🚧 How It Works

1. **URL Analysis:** Extracts and computes numerical features from a given URL.
2. **Label Generation:** Assigns labels to URLs based on their characteristics, necessary for supervised learning.
3. **Integration:** These features and labels are passed on to the **Prediction Engine** for making predictions.

## 🔮 Prediction Engine

The **Prediction Engine** is a Flask microservice designed to generate predictions using the latest trained models. It works in coordination with the Features Processor Engine and provides a streamlined prediction service.

- Uses the URL data provided by the Frontend Client to generate predictions.
- Retrieves the most recent model from the database to ensure accurate predictions.
- Updates the **New Sampled Rows** table with the prediction data for new URLs.

### 🛠 How It Works

1. **Feature Gathering:** Requests features from the **Features Processor Engine**.
2. **Prediction:** Uses the ML model to generate a prediction for the provided URL.
3. **Data Storage:** Updates the database with both feature data and prediction results for further analysis.

## 🌐 Deployment on Google Cloud Run

The entire Data Server Engine is designed to be hosted on **Google Cloud Run** using Dockerized images for each microservice.

- 🐳 **Dockerized Deployment**: Each microservice runs in a separate container for easy deployment and scalability.
- ☁️ **Cloud-Ready**: Deployed using CI/CD pipelines to ensure seamless integration and continuous delivery.

## 🚀 Getting Started

### 1. Prerequisites

Ensure you have the following installed:

- 🐍 Python 3.8+
- 📦 Docker
- ☁️ Google Cloud SDK

### 2. Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/data-server-engine.git
   cd data-server-engine
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Running the Services Locally

- **Start the gRPC server**:

  ```bash
  python grpc/grpc_server.py
  ```

- **Run the Flask app**:
  ```bash
  python app/main.py
  ```

### 4. Building and Deploying with Docker

1. **Build the Docker image**:

   ```bash
   docker build -t data-server-engine .
   ```

2. **Run the Docker container**:
   ```bash
   docker run -p 5000:5000 data-server-engine
   ```

## 📖 API Endpoints

### Features Processor Engine Endpoints

- `/features/unusual-extensions` - Generate features for unusual extensions
- `/features/typosquatting` - Generate features for typosquatting detection
- `/features/phishing` - Generate features for phishing detection
- `/label` - Generate labels for URLs

### Prediction Engine Endpoint

- `/predict` - Generate a prediction using the trained model

## 🛠 Tech Stack

- **Backend Framework**: Flask
- **Inter-Service Communication**: gRPC
- **Containerization**: Docker
- **Hosting**: Google Cloud Run
- **ML Models**: Integrated with real-time data processing

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [gRPC Documentation](https://grpc.io/docs/)
- [Google Cloud Run](https://cloud.google.com/run/docs)

## 👥 Contributors

- **Your Name** - [GitHub Profile](https://github.com/your-username)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check out the [issues page](https://github.com/your-username/data-server-engine/issues).

### 🙏 Acknowledgments

Special thanks to all the contributors and the open-source community for their amazing tools and libraries.
