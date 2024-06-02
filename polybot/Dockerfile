# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Copy the PEM files into the working directory
COPY private.pem .
COPY YOURPUBLIC.pem .

# Expose the port
EXPOSE 8443

# Command to run the application
CMD ["python", "app.py"]
