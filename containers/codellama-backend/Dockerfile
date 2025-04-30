# Use a Python 3.10 base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu \
    transformers==4.31.0 \
    fastapi==0.103.0 \
    uvicorn==0.23.2 \
    accelerate==0.21.0 \
    bitsandbytes==0.41.0

# Copy the application code
COPY app.py .

# Expose the FastAPI port
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "app.py:app", "--host", "0.0.0.0", "--port", "8000"]