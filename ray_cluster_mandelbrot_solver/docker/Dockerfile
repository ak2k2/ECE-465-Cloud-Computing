# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code and the DB directory
COPY src/ .

# Flask and Ray
EXPOSE 5010
EXPOSE 6379-6381 8265 10001-10999


# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
