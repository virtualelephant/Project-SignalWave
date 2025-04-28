# Ubuntu System Metrics Collector

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

## Directory Structure

```bash
ubuntu-system-metrics/
├── metrics_collector.py
├── config.yaml
├── requirements.txt
└── systemd/
    └── metrics-collector.service
```

---

## Installation Instructions

### 1. Clone or Download the Repository

```bash
cd /opt
sudo git clone <repo-url> ubuntu-system-metrics
cd ubuntu-system-metrics
```

### 2. Create and Activate a Virtual Environment (Optional but Recommended)

```bash
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Requirements

```bash
pip install -r requirements.txt
```

### 4. Configure InfluxDB Connection

Edit `config.yaml`:

```yaml
influxdb:
  url: "http://your-influxdb-server:8086"
  token: "your-token"
  org: "your-org"
  bucket: "monitoring"

poll_interval_minutes: 1  # Options: 1, 3, or 5
```

### 5. Setup systemd Service

```bash
sudo cp systemd/metrics-collector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable metrics-collector
sudo systemctl start metrics-collector
```

To check service status:

```bash
sudo systemctl status metrics-collector
```

---

## Troubleshooting

- Check logs via `journalctl`:

```bash
sudo journalctl -u metrics-collector -f
```

- Ensure the InfluxDB URL, token, and organization are correct in `config.yaml`
- Make sure the VM can reach InfluxDB over the network.

---

## Roadmap (Future Enhancements)

- Per-interface network metrics
- Per-disk device metrics
- System uptime collection
- Docker container packaging
- Healthcheck endpoint

---

## License

MIT License

---

## Author

Virtual Elephant Consulting, LLC

> "Designed for home labs, built for enterprise scalability."

