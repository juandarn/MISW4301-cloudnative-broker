FROM python:3.11-alpine

# Install system dependencies
RUN apk add --no-cache gcc musl-dev postgresql-dev

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src

# Set environment variables
ENV PYTHONPATH=/app/src
ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "-c", "from src.app import create_app; app = create_app(); app.run(host='0.0.0.0', port=5000, debug=True)"]
