# =========================
# Base image
# =========================
FROM python:3.10-slim

# =========================
# Set working directory
# =========================
WORKDIR /app

# =========================
# Install backend dependencies
# =========================
COPY ./Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =========================
# Copy backend and frontend code
# =========================
COPY ./Backend/ ./backend
COPY ./frontend/ ./frontend

# =========================
# Expose port
# =========================
EXPOSE 8000

# =========================
# Set environment variables (optional)
# =========================
ENV PORT=8000
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

# =========================
# Start Gunicorn server
# =========================
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.app:app"]

