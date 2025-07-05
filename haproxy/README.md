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

## Rancher Updates

Edit the cluster YAML

```yaml
spec:
  rkeConfig:
    machineGlobalConfig:
      cni: cilium
      disable-kube-proxy: false
      etcd-expose-metrics: false
      tls-san:
        - "10.5.1.13"
```

Test the update after Rancher has completed updating the controller nodes

```bash
echo | openssl s_client -connect 10.5.1.13:6443 -servername kubernetes | openssl x509 -noout -text | grep -A1 "Subject Alternative Name"
```

Get the intermediate Root CA cert that Rancher created

```bash
openssl s_client -connect 10.5.1.13:6443 -showcerts </dev/null
```

Create a HAProxy User for the new `kubeconfig` file to leverage

```bash
kubectl create serviceaccount haproxy-user -n kube-system
kubectl create clusterrolebinding haproxy-user-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:haproxy-user
kubectl -n kube-system create token haproxy-user
```

Copy the output similar to:

```bash
eyJhbGciOiJSUzI1NiIsImtpZCI6Ijl6YVNSRnZpaXNfdVBhTlc4cU5ldkp1b1RtNF9PV0IzdG5Cbm9TeTlNcjgifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiLCJya2UyIl0sImV4cCI6MTc1MTU2MDg5MSwiaWF0IjoxNzUxNTU3MjkxLCJpc3MiOiJodHRwczovL2t1YmVybmV0ZXMuZGVmYXVsdC5zdmMuY2x1c3Rlci5sb2NhbCIsImp0aSI6ImMzYWEwOThiLWJkZGMtNDJkYy1hYTg1LTc2MzlkYTYwMWE1NyIsImt1YmVybmV0ZXMuaW8iOnsibmFtZXNwYWNlIjoia3ViZS1zeXN0ZW0iLCJzZXJ2aWNlYWNjb3VudCI6eyJuYW1lIjoiaGFwcm94eS11c2VyIiwidWlkIjoiMTA0NTZkZDQtNjNkMi00ZjljLWIxZDUtYzU4MzYyODFhYWRiIn19LCJuYmYiOjE3NTE1NTcyOTEsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlLXN5c3RlbTpoYXByb3h5LXVzZXIifQ.PJH4jLUGZl2MzJSsmsYQd2j0oEfeZnzkFq-xUjhYUm_ojyoOG3jBE7c_7Z9h5N1sVM78KY7-v-ww2yqqWZ61BtdtrNmBPs-MozxhKKWlgTGZLdtMCB_D5iU4cxtvck_Le8nh8eUftQcR-0P64RyAA2gVvXRbhGsUXEniPFw_dbVjjM1_k59v4txEU7OwMg9HvltSG_CaLAOVPz3cyrqkn1EvsLVG9pqEy9Ou8rcWkanK1UautX4IYiNR456BnaX8rBsA69UpmbcwWrKL1DoWs-EjF746vOCMJevg6E6NmYHE-89_niqVpES1ZVKnUc-RGrQ6G-g10iZMdRrzfGncpg
```

Look for the `rke2-server-ca@` chain and you need to copy that certificate into a file that you will reference as the certificate authority in the `kubeconfig` file.

```bash
openssl s_client -connect 10.5.1.13:6443 -showcerts </dev/null
```

```bash
 1 s:CN = rke2-server-ca@1751559400
   i:CN = rke2-server-ca@1751559400
   a:PKEY: id-ecPublicKey, 256 (bit); sigalg: ecdsa-with-SHA256
   v:NotBefore: Jul  3 16:16:40 2025 GMT; NotAfter: Jul  1 16:16:40 2035 GMT
-----BEGIN CERTIFICATE-----
MIIBejCCAR+gAwIBAgIBADAKBggqhkjOPQQDAjAkMSIwIAYDVQQDDBlya2UyLXNl
cnZlci1jYUAxNzUxNTU5NDAwMB4XDTI1MDcwMzE2MTY0MFoXDTM1MDcwMTE2MTY0
MFowJDEiMCAGA1UEAwwZcmtlMi1zZXJ2ZXItY2FAMTc1MTU1OTQwMDBZMBMGByqG
SM49AgEGCCqGSM49AwEHA0IABMOP0rVCrofEZYH3tdv6SNO5o9t7+13AyagkcrWw
was++wmE0HsSJfrE9+LpD8U+lrEqsEcN3EREGNI4n+0fucSjQjBAMA4GA1UdDwEB
/wQEAwICpDAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBQrc2jrzqAW9ZRC4eEs
HnHkJUlOsTAKBggqhkjOPQQDAgNJADBGAiEAw6+/e/RCMCHBUZ10SUlkvrVwa9t5
eI6oM9VPjMrhvsICIQCqXG3ytlPKO894roFKKEsjIPbKaZ3eKIkSRn+GrzoCZg==
-----END CERTIFICATE-----
```

Edit the new `kubeconfig` file:

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority: /home/deploy/haproxy/cluster-ca.crt
    server: https://10.5.1.13:6443
  name: dev
contexts:
- context:
    cluster: dev
    user: haproxy-user
  name: haproxy-context
current-context: haproxy-context
kind: Config
users:
- name: haproxy-user
  user:
    token: eyJhbGciOiJSUzI1NiIsImtpZCI6Ijl6YVNSRnZpaXNfdVBhTlc4cU5ldkp1b1RtNF9PV0IzdG5Cbm9TeTlNcjgifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiLCJya2UyIl0sImV4cCI6MTc1MTU2MDg5MSwiaWF0IjoxNzUxNTU3MjkxLCJpc3MiOiJodHRwczovL2t1YmVybmV0ZXMuZGVmYXVsdC5zdmMuY2x1c3Rlci5sb2NhbCIsImp0aSI6ImMzYWEwOThiLWJkZGMtNDJkYy1hYTg1LTc2MzlkYTYwMWE1NyIsImt1YmVybmV0ZXMuaW8iOnsibmFtZXNwYWNlIjoia3ViZS1zeXN0ZW0iLCJzZXJ2aWNlYWNjb3VudCI6eyJuYW1lIjoiaGFwcm94eS11c2VyIiwidWlkIjoiMTA0NTZkZDQtNjNkMi00ZjljLWIxZDUtYzU4MzYyODFhYWRiIn19LCJuYmYiOjE3NTE1NTcyOTEsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlLXN5c3RlbTpoYXByb3h5LXVzZXIifQ.PJH4jLUGZl2MzJSsmsYQd2j0oEfeZnzkFq-xUjhYUm_ojyoOG3jBE7c_7Z9h5N1sVM78KY7-v-ww2yqqWZ61BtdtrNmBPs-MozxhKKWlgTGZLdtMCB_D5iU4cxtvck_Le8nh8eUftQcR-0P64RyAA2gVvXRbhGsUXEniPFw_dbVjjM1_k59v4txEU7OwMg9HvltSG_CaLAOVPz3cyrqkn1EvsLVG9pqEy9Ou8rcWkanK1UautX4IYiNR456BnaX8rBsA69UpmbcwWrKL1DoWs-EjF746vOCMJevg6E6NmYHE-89_niqVpES1ZVKnUc-RGrQ6G-g10iZMdRrzfGncpg
```