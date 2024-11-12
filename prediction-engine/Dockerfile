FROM python:3.9-slim
WORKDIR /prediction-engine
# Install required tools and dependencies for building
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*
# Install the specific version of protoc (28.2)
RUN wget https://github.com/protocolbuffers/protobuf/releases/download/v28.2/protoc-28.2-linux-x86_64.zip -O protoc.zip \
    && unzip protoc.zip -d /usr/local \
    && rm protoc.zip
# Add /usr/local/bin to the PATH for protoc
ENV PATH="$PATH:/usr/local/bin"
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
# Set PYTHONPATH to include the root of your project
ENV PYTHONPATH=/prediction-engine
COPY . .
# Expose both Flask and gRPC port
EXPOSE 5001 50051
CMD ["python", "main.py"]
