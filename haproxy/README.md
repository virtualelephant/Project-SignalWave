# HAProxy Configurations and Scripts to support Rancher

Rancher leverages a reverse proxy for accessing external services running inside the Kubernetes cluster. There is a need to implement a more robust, production-ready load balancer for handling application traffic running inside the Kubernetes cluster itself. Leveraging an external HAProxy load balancer will allow us to achieve a greater HA service offering.

Have HAProxy:

* Use a static frontend IP or VIP to receive traffic (L4 or L7).
* Automatically route that traffic to Kubernetes pods or services without hardcoding node IPs, even as nodes scale or churn.
* Optionally serve multiple services via path-based routing (L7) or TCP load balancing (L4).

## HAProxy VM

The HAProxy VM is a light-weight virtual machine running inside the VMware VCF environment. It is currently configured with the following specs:

* 1 vCPU
* 2GB RAM
* 75GB Disk
* Management NIC
* Tenant NIC

HAProxy will be configured to bind all Kubernetes HTTP and HTTPS traffic to the Tenant NIC that is attached to a dedicated NSX network segment for VIPs.

## HAProxy Config Generation Script

Because Rancher can and will redeploy new VMs as part of the typical LCM, the IP addresses of both the controllers and worker nodes will change over time. The HAProxy setup needs to be able to detect and update its config based on those LCM changes. The `generate-haproxy-cfg.sh` script should be setup to run once per minute, through CRON, to detect these dynamic changes.

```bash
cp generate-haproxy-cfg.sh /usr/local/bin/
chmod +x /usr/local/bin/generate-haproxy-cfg.sh
```