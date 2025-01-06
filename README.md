# Project-SignalWave
Project SignalWave is a modern, cloud-native application designed to demonstrate the implementation of microservices architectures within a Kubernetes cluster.
It integrates advanced observability tools and provides a real-world example of how to manage message queues, monitor application performance, and build scalable, resilient systems.

This project is ideal for developers, architects, and DevOps engineers looking to understand and implement best practices for cloud-native development and operations.


# Features

## Network Observability Metrics

The **SignalWave Publisher** application is designed with integrated network observability, providing detailed insights into its performance and interactions within the broader SignalWave microservices architecture. Below is an overview of the key metrics collected and exposed for monitoring via Prometheus:

### Exposed Metrics

1. **Request Metrics**
   - **Total Requests (`http_requests_total`):** The cumulative count of HTTP requests received by the application.
   - **Request Duration (`http_request_duration_seconds`):** Histogram of the time taken to process requests, enabling latency analysis.
   - **Request Size (`http_request_size_bytes`):** Histogram of the size of incoming HTTP requests.

2. **Response Metrics**
   - **Response Status Codes (`http_response_status`):** Count of HTTP responses grouped by status codes (e.g., 2xx, 4xx, 5xx).
   - **Response Duration (`http_response_duration_seconds`):** Histogram of the time taken to send responses to clients.
   - **Response Size (`http_response_size_bytes`):** Histogram of the size of responses sent.

3. **Network Traffic Metrics**
   - **Incoming Traffic (`network_in_bytes`):** Total number of bytes received by the application.
   - **Outgoing Traffic (`network_out_bytes`):** Total number of bytes transmitted by the application.
   - **Connection Metrics (`tcp_active_connections`):** Current count of active TCP connections.

4. **Error Metrics**
   - **Request Errors (`http_request_errors_total`):** Total count of failed HTTP requests due to client or server errors.
   - **Connection Errors (`network_connection_errors_total`):** Count of failed network connection attempts.

5. **Custom Metrics**
   - **Publisher-Specific Events (`publisher_events_total`):** Total number of events published to downstream services or message queues.
   - **Latency Metrics (`publisher_event_latency_seconds`):** Histogram of event latency, tracking the time between event generation and publishing.

### Integration with Prometheus

The metrics are exposed at the `/metrics` endpoint on port `8080`. Prometheus scrapes these metrics at regular intervals to enable real-time monitoring and alerting. To configure Prometheus scraping for this service, the following annotations are applied in the Kubernetes deployment:
```
prometheus.io/scrape: "true"
prometheus.io/path: "/metrics"
prometheus.io/port: "8080"
```

## Microservices Architecture:

- A Publisher Service for generating and publishing messages to RabbitMQ.
- A Reader Service consumes and processes messages dynamically.
- A Frontend Service displays logs in real-time via an enhanced NGINX-hosted HTML page.

## Observability:

- Structured logging using Fluentd, Elasticsearch, and Kibana (EFK stack).
- Custom metrics collection using Prometheus and visualized in Grafana.

## Scalability and Monitoring:

- Demonstrates scalable messaging with RabbitMQ.
- Exposes Prometheus metrics to monitor message queue depth, worker throughput, and application latency.

## Cloud-Native Technologies:

- Built on Kubernetes with containers orchestrated for high availability.
- Incorporates best practices for logging, monitoring, and application observability.

# Use Cases
## Learning and Training:

- Understand Kubernetes, RabbitMQ, and observability tools.
- Learn how to build scalable, cloud-native microservices.

## Demo Environment:

- Showcase modern application development and deployment.
- Highlight observability and performance monitoring in action.

## Prototype Development:

Use as a base for developing advanced microservices.

## Technology Stack

- Messaging: RabbitMQ
- Monitoring: Prometheus, Grafana
- Logging: Fluentd, Elasticsearch, Kibana
- Frontend: NGINX with a dynamic log display
- Containerization: Docker
- Orchestration: Kubernetes