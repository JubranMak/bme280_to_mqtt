# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app


# Install git to clone the repository
RUN apt-get update && apt-get install -y git && apt-get clean


# Clone the repository (replace <REPO_URL> with the actual Git repository URL)
RUN git clone "https://github.com/JubranMak/bme280_to_mqtt.git" .

# Install Python dependencies if a requirements.txt file exists
RUN pip install --no-cache-dir -r requirements.txt || echo "No dependencies"

# Entry point to pass MQTT arguments
ENTRYPOINT ["python", "main.py"]
