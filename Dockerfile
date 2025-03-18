# Use the official Python image
FROM python:3.13

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents to the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]

