# Stage 1: Build React frontend
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY pkg/frontend/package.json pkg/frontend/package-lock.json ./
RUN npm install
COPY pkg/frontend .
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libgl1 libglib2.0-0

WORKDIR /app

# Copy backend files
COPY pkg/backend .

# Install Python dependencies
COPY pkg/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend build into the backend's static folder
COPY --from=frontend-build /app/frontend/build ./pkg/frontend/build

# Expose Flask port
EXPOSE 5000

# Start Flask app
CMD ["python", "app.py"]
