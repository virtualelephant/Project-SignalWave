# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app
COPY mtg-card-sync.py /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Add a cron job to run the script hourly
RUN apt-get update && \
    apt-get install -y cron
RUN echo "0 * * * * /usr/local/bin/python /app/mtg-card-sync.py >> /var/log/cron.log 2>&1" > /etc/cron.d/mtg-card-sync && \
    chmod 0644 /etc/cron.d/mtg-card-sync && \
    crontab /etc/cron.d/mtg-card-sync && \
    touch /var/log/cron.log

# Ensure cron runs in the foreground
CMD ["cron", "-f"]
#CMD ["tail", "-f", "/dev/null"]
