# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY src/ .

# Set main.py as the entry point of the container
CMD ["python", "main.py"]
