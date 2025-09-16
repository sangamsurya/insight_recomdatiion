# Dockerfile for the scheduled scripts
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy and install the dependencies for the scripts
COPY ./scripts/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the scripts themselves
COPY ./scripts/ .

# Define the default command to run your script
CMD ["python", "run_scripts.py"]