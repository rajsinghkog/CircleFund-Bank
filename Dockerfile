# Use official Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Node.js for frontend build
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY pyproject.toml uv.lock ./
RUN pip install --upgrade pip && pip install --no-cache-dir 'uv'
RUN uv sync --locked

# Copy backend code
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

# Copy frontend and build it
COPY frontend/ ./frontend/
WORKDIR /app/frontend
RUN npm install && npm run build

# Move built frontend to static
RUN cp -r build/* /app/static/
WORKDIR /app

# Expose port
EXPOSE 8000

# Start FastAPI app
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
