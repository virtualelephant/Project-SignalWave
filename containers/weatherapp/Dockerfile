FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and cities file
COPY historical_weather.py .
COPY current_weather.py .
COPY cities.txt .

#CMD ["python", "historical_weather.py"]
CMD ["tail", "-f", "/dev/null"]