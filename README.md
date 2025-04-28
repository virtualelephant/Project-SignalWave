# Project-SignalWave
Project SignalWave started out as a simple demo application for a micro-services application and has grown to be a complete Kubernetes cluster with a set of shared services
and monitoring systems. The repo provides directions for installing the following shared or monitoring services:

* Prometheus with Grafana
* Longhorn
* InfluxDB
* RabbitMQ
* ELK (ElasticSearch, Fluentd, Kibana)

Each of these applications are installed using Helm with values files provided based on how I run it within my Kubernetes clusters. In addition, where necessary there
are also ingress YAML files for each service that needs to be exposed externally. These are intended to be run in production or a production-like environment, this is not
intended to install these applications within a Kind cluster or run on a laptop.

This project is ideal for developers, architects, and DevOps engineers looking to understand and implement best practices for cloud-native development and operations.

# Repo Structure

- Containers
- Core-Services
- Grafana-Dashboards
- PowerCLI
- Python
- YAML

---
# Containers
These are the containers used by many of the applications running within the Kubernetes clusters. These containers are leveraged for various activities, some are actual
applications running or providing a service, others are used for monitoring various aspects of both the physical infrastructure and the VMware Cloud Foundation supporting
software components.

- cisco-snmp: `READY` Container for monitoring physical network devices over SNMP.
- fping: `READY` Container for testing external connectivity to a set of user-specified endpoints.
- mtg-publisher: `READY` Container for pulling Magic:The Gathering cards off public API and pushing them to RabbitMQ.
- signalwave-publisher: `READY` Container for getting external connectivity metrics to website and pushing them to RabbitMQ.
- signalwave-reader: `READY` Container for pulling metrics off of RabbitMQ and publishing to InfluxDB.
- weatherapp: `WIP` Container for gathering weather information for a set of user-specified endpoints.

---
# Grafana Dashboards
Project SignalWave provides a set of dasbhoards that show off the core components of the Kubernetes cluster and the applications running within it. These may need to be modified
based on the container repository you use, as well as panel names based on your physical hardware.

## Main Dashboard
![Alt text](images/grafana-main-dashboard.png)

## Cisco Dashboard
![Alt text](images/grafana-cisco-dashboard.png)

---
# Linux System Metrics Collector

A lightweight Python application that runs on an Ubuntu VM, gathers detailed system metrics, and pushes them into InfluxDB.

Ideal for building a small, efficient observability stack without the overhead of full monitoring agents.

---

## Features

- Collects detailed CPU, Memory, Disk, and Network statistics
- Pushes metrics to InfluxDB (single write per polling cycle)
- Configurable polling interval: **1, 3, or 5 minutes**
- Runs automatically on boot via **systemd**
- Lightweight and easy to extend

---

## Metrics Collected

### CPU
- Total CPU utilization (%)
- Per-core CPU utilization (%)
- Load average over 1, 5, and 15 minutes

### Memory
- Memory usage (%)
- Total Memory (MB)
- Used Memory (MB)
- Free Memory (MB)
- Cached Memory (MB)

### Disk
- Disk usage (%)
- Disk total size (GB)
- Disk used space (GB)
- Disk free space (GB)
- Disk read bytes
- Disk write bytes

### Network
- Total bytes sent
- Total bytes received
- Total packets sent
- Total packets received
- Network errors in
- Network errors out

All metrics are tagged with the **hostname** of the VM for easy multi-host aggregation.

---
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
- Monitoring: Prometheus, Grafana, InfluxDB
- Logging: Fluentd, Elasticsearch, Kibana
- Containerization: Docker
- Orchestration: Kubernetes