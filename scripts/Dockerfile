# Use the official Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies for the backend service
COPY ./Backend/requirements.txt ./Backend/
RUN pip install --no-cache-dir -r ./Backend/requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port that Gunicorn will run on
EXPOSE $PORT

# Run the Flask app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "Backend.flask_app:app"]