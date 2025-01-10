FROM nginx:latest

# Copy NGINX config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static files
COPY index.html /usr/share/nginx/html/

# Link the graph directory to the NGINX root
RUN mkdir -p /usr/share/nginx/html/graphs

# Expose the container's port
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]
