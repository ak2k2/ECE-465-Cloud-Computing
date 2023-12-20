# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /usr/src/app

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    ocl-icd-libopencl1 \
    clinfo \
    apt-utils \
    unzip \
    tar \
    curl \
    xz-utils \
    opencl-headers \
    intel-opencl-icd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code and the DB directory
COPY src/ .

# Expose the port the app runs on
EXPOSE 5010

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
