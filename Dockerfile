# Use python official image (slim version for better compatibility with wheels)
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /src
ENV PYTHONPATH=/src

# Install OpenCV system dependencies
RUN apt-get update && apt-get install -y \
libgl1 \
libglib2.0-0 \
&& rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt and install the dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy the rest of application code
COPY . .

# Define the commands to run the application
CMD ["python", "main.py"]