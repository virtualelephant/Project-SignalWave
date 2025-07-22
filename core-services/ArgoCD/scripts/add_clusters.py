import base64
import os
from kubernetes import client, config
import yaml

# Configuration
clusters = [
    {"name": "dev-cluster", "kubeconfig": "/path/to/dev-config", "server": "https://dev-cluster-api:6443"},
    {"name": "stage-cluster", "kubeconfig": "/path/to/stage-config", "server": "https://stage-cluster-api:6443"},
    {"name": "prod-cluster", "kubeconfig": "/path/to/prod-config", "server": "https://prod-cluster-api:6443"},
]
argocd_namespace = "argocd"

def get_cluster_credentials(kubeconfig_path):
    """Extract CA certificate and token from kubeconfig."""
    config.load_kube_config(config_file=kubeconfig_path)
    v1 = client.CoreV1Api()
    
    # Create ServiceAccount and ClusterRoleBinding
    sa = client.V1ServiceAccount(metadata=client.V1ObjectMeta(name="argocd-manager", namespace="kube-system"))
    try:
        v1.create_namespaced_service_account(namespace="kube-system", body=sa)
    except client.ApiException as e:
        if e.status != 409:  # Ignore if already exists
            raise

    # Create ClusterRole and ClusterRoleBinding (simplified, adjust permissions as needed)
    role = client.V1ClusterRole(
        metadata=client.V1ObjectMeta(name="argocd-manager-role"),
        rules=[client.V1PolicyRule(api_groups=["*"], resources=["*"], verbs=["*"])]
    )
    try:
        client.RbacAuthorizationV1Api().create_cluster_role(body=role)
    except client.ApiException as e:
        if e.status != 409:
            raise

    binding = client.V1ClusterRoleBinding(
        metadata=client.V1ObjectMeta(name="argocd-manager-role-binding"),
        subjects=[client.V1Subject(kind="ServiceAccount", name="argocd-manager", namespace="kube-system")],
        role_ref=client.V1RoleRef(api_group="rbac.authorization.k8s.io", kind="ClusterRole", name="argocd-manager-role")
    )
    try:
        client.RbacAuthorizationV1Api().create_cluster_role_binding(body=binding)
    except client.ApiException as e:
        if e.status != 409:
            raise

    # Get ServiceAccount token
    secret = v1.list_namespaced_secret(namespace="kube-system", field_selector="metadata.annotations.kubernetes\\.io/service-account\\.name=argocd-manager")
    token = base64.b64decode(secret.items[0].data["token"]).decode("utf-8")
    ca_cert = base64.b64decode(secret.items[0].data["ca.crt"]).decode("utf-8")
    return token, ca_cert

def create_argocd_cluster_secret(cluster):
    """Create ArgoCD cluster secret YAML."""
    token, ca_cert = get_cluster_credentials(cluster["kubeconfig"])
    secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": f"cluster-{cluster['name']}",
            "namespace": argocd_namespace,
            "labels": {"argocd.argoproj.io/secret-type": "cluster"}
        },
        "stringData": {
            "name": cluster["name"],
            "server": cluster["server"],
            "config": yaml.dump({
                "bearerToken": token,
                "tlsClientConfig": {"caData": ca_cert}
            })
        }
    }
    with open(f"cluster-{cluster['name']}-secret.yaml", "w") as f:
        yaml.safe_dump(secret, f)
    os.system(f"kubectl apply -f cluster-{cluster['name']}-secret.yaml")

def main():
    for cluster in clusters:
        try:
            create_argocd_cluster_secret(cluster)
            print(f"Successfully added {cluster['name']} to ArgoCD")
        except Exception as e:
            print(f"Failed to add {cluster['name']}: {str(e)}")

if __name__ == "__main__":
    main()