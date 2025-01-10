FROM nginx:latest

# Install necessary packages
RUN apt-get update && apt-get install -y \
    rrdtool \
    python3 \
    python3-rrdtool \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the graph generation script
COPY generate-graphs.py /app/

# Set up the directories
RUN mkdir -p /app/rrd_files /app/graphs

# Set up a cron job to generate graphs every 5 minutes
RUN echo "*/5 * * * * root python3 /app/generate-graphs.py" >> /etc/crontab

# Copy NGINX configuration if you have custom settings
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the directory with graphs
RUN ln -s /app/graphs /usr/share/nginx/html/graphs

# Start cron and NGINX
CMD service cron start && nginx -g 'daemon off;'
