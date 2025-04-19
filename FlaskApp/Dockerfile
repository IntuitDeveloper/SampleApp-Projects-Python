# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt



# Expose the port your app runs on
EXPOSE 5001




# Define the command to run the application
CMD ["python", "app.py"]

