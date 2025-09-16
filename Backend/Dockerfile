FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY ./Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend build
COPY ./Backend/ ./backend
COPY ./frontend/ ./frontend

# Expose port
EXPOSE 8000

# Environment variables
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

# Run Gunicorn using Railway's $PORT
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT backend.app:app"]
