# Use an official Python runtime as a parent image
FROM python:3.11-slim
# Set environment variables to help detect Docker environment
ENV DOCKER_ENV=true

# Alternatively, you could use CI if your Docker setup is also used in CI/CD pipelines
# ENV CI=true
# Set the working directory in the container
WORKDIR /app

# Install dependencies needed to download files
RUN apt-get update && apt-get install -y \
    wget \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for your GitHub repository and release
    
# Install dependencies for .NET
RUN apt-get update && apt-get install -y \
    wget \
    apt-transport-https \
    software-properties-common

# Add Microsoft package signing key and repository
RUN wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb

# Install the .NET SDK and Runtime
RUN apt-get update && apt-get install -y \
    dotnet-sdk-6.0 \
    dotnet-runtime-6.0

RUN pip install https://github.com/qctrader/qcTrader/releases/download/v1.0-beta.1/qcTrader-1.1.7-py3-none-any.whl    

COPY . ./app 


# Run the application to see if the package is working correctly
CMD ["python", "/app/app/example_script.py"]
