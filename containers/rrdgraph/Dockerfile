# Base image
FROM harbor.home.virtualelephant.com/ve-lab/rrdtool:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Set up the directories
RUN mkdir -p /app/rrd_files
RUN mkdir -p /app/graphs

# Copy the graph generation script
COPY generate-graphs.py /app/

# Run the script in an infinite loop
#CMD ["python3", "/app/generate-graphs.py"]
CMD ["tail", "-f", "/dev/null"]
