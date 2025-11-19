FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including ALL libraries for RDKit
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libxrender1 \
    libxext6 \
    libsm6 \
    libexpat1 \
    libgomp1 \
    libxinerama1 \
    libxi6 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
