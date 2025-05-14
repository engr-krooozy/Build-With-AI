# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Make port 8080 available to the world outside this container
# This is the default port Uvicorn will run on if PORT env var is not set
EXPOSE 8080

# Define environment variable for the port (optional, can be overridden by Cloud Run)
ENV PORT 8080

# Run main.py when the container launches
# Use uvicorn to run the FastAPI application
# --host 0.0.0.0 makes the server accessible from outside the container
# --port $PORT uses the environment variable for port configuration
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
