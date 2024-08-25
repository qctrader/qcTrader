# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app
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
    
COPY . ./app
# # Install dependencies (optional, if you have any)
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# Install the package from TestPyPI
RUN pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple qcTrader==1.1.0

# Run the application to see if the package is working correctly
CMD ["python", "app/example_script.py"]
