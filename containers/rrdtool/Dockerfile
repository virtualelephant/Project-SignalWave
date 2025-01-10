# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy script and install dependencies
COPY rrd-reader.py /app/
RUN pip install pika rrdtool

# Create necessary directories
RUN mkdir -p /app/rrd_files

# Run the script
CMD ["python", "rrd-reader.py"]
