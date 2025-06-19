# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-build

WORKDIR /app

# Only copy files needed for npm install
COPY pkg/frontend/package.json pkg/frontend/package-lock.json ./
RUN npm install

# Copy the rest of the frontend code
COPY pkg/frontend .
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim

WORKDIR /app

# Copy backend code
COPY pkg/backend .

# Install Python dependencies
COPY pkg/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the React build (static files) into backend's static folder
COPY --from=frontend-build /app/build ./pkg/frontend/build

# Expose backend port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
