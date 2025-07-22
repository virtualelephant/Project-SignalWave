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

- Ansible
- Containers
- Core-Services
- Grafana-Dashboards
- PowerCLI
- Python
- YAML

---
# Ansible
`WIP` Ansible playbooks for standing up a Kubernetes environment identical to the version running inside my home lab environment. Uses the Helm repos for standing up all the required services to support Project SignalWave and all of it's components.

---
# Containers
These are the containers used by many of the applications running within the Kubernetes clusters. These containers are leveraged for various activities, some are actual
applications running or providing a service, others are used for monitoring various aspects of both the physical infrastructure and the VMware Cloud Foundation supporting
software components.

- cisco-snmp: `READY` Container for monitoring physical network devices over SNMP.
- codellama-backend: `WIP` Container for running the CodeLlama-7B model locally.
- codellama-frontend: `WIP` Container for interacting with locally running CodeLlama-7B model.
- fping: `READY` Container for testing external connectivity to a set of user-specified endpoints.
- mtg-publisher: `READY` Container for pulling Magic:The Gathering cards off public API and pushing them to RabbitMQ.
- python-debug: `READY` Container for testing Python code in an isolated environment that can edit files and pull directly from a Git repo.
- signalwave-publisher: `READY` Container for getting external connectivity metrics to website and pushing them to RabbitMQ.
- signalwave-reader: `READY` Container for pulling metrics off of RabbitMQ and publishing to InfluxDB.
- weatherapp: `WIP` Container for gathering weather information for a set of user-specified endpoints.

---
# Python

## Linux System Metrics Collector

A lightweight Python application that runs on an Ubuntu VM, gathers detailed system metrics, and pushes them into InfluxDB.

Ideal for building a small, efficient observability stack without the overhead of full monitoring agents.

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