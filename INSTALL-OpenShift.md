# Caveats for running Project SignalWave in Red Hat OpenShift

## Installing the NFS Provisioner
```bash
helm install nfs-subdir-external-provisioner \
  nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  --namespace nfs-storage \
  --set nfs.server=nfs.home.virtualelephant.com \
  --set nfs.path=/opt/nfs/rhos \
  --set storageClass.name=nfs-sc \
  --set storageClass.defaultClass=true \
  --set podSecurityContext.runAsUser=1001 \
  --set podSecurityContext.runAsGroup=1001 \
  --set podSecurityContext.fsGroup=1001 \
  --set podSecurityContext.fsGroupChangePolicy="OnRootMismatch" \
  --set podSecurityContext.runAsNonRoot=true \
  --set podSecurityContext.seccompProfile.type=RuntimeDefault \
  --set securityContext.allowPrivilegeEscalation=false \
  --set securityContext.capabilities.drop[0]=ALL
```

```bash
oc adm policy add-scc-to-user hostmount-anyuid system:serviceaccount:nfs-storage:nfs-subdir-external-provisioner
oc adm policy add-scc-to-user privileged system:serviceaccount:nfs-storage:nfs-subdir-external-provisioner
oc rollout restart deployment/nfs-subdir-external-provisioner -n nfs-storage
```

## Harbor repo for Global Pull Secret

```bash
oc create secret docker-registry harbor-global-secret \
  --docker-server=harbor.home.virtualelephant.com \
  --docker-username=admin \
  --docker-password=thAswU53n-CE \
  --docker-email=admin@harbor.home.virtualelephant.com \
  -n openshift-config
oc get secret/pull-secret -n openshift-config -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d > pull-secret.json
```

### Edit the pull-secret.json

```json
{
        "auths":{
                "harbor.home.virtualelephant.com": {
                        "auth": "YWRtaW46dGhBc3dVNTNuLUNF",
                        "email": "admin@harbor.home.virtualelephant.com"
                },
                "cloud.openshift.com":{
                        "auth":"b3BlbnNoaWZ0LXJlbGVhc2UtZGV2K29jbV9hY2Nlc3NfZDdjYjNlNzgzNjA4NDI3MmE3ZDI4NmYzYzFkYmE1M2E6SzNZNVZTNEpZNUpMVFhPN0FQQ0RNWkU4WFZOUjVYUjJGVldNRjFMR1ZZQjdQSDZZUkFDQVc5UjNKUlBKUjQ3Mw==",
                        "email":"chris@virtualelephant.com"
                },
                "quay.io":{
                        "auth":"b3BlbnNoaWZ0LXJlbGVhc2UtZGV2K29jbV9hY2Nlc3NfZDdjYjNlNzgzNjA4NDI3MmE3ZDI4NmYzYzFkYmE1M2E6SzNZNVZTNEpZNUpMVFhPN0FQQ0RNWkU4WFZOUjVYUjJGVldNRjFMR1ZZQjdQSDZZUkFDQVc5UjNKUlBKUjQ3Mw==",
                        "email":"chris@virtualelephant.com"
                },
                "registry.connect.redhat.com":{
                        "auth":"fHVoYy1wb29sLTU3MGJiY2E2LTMyMjQtNDg0Ni04NzEwLTUxOGExMWVkOWI0ZDpleUpoYkdjaU9pSlNVelV4TWlKOS5leUp6ZFdJaU9pSXpNekEwT0dRMk5EQmtaalkwTWpoaE9XTmpOVGhqTkdWaE9EQTVOMlJtTUNKOS53d2ZjNzctS3J4dUUzMktHS1NKNGtldUtjWWZXMGRRX0VzX252OHNyeldDenlaS2gycUhtTEMzZjdUeUxSUm5leW0teDdZWHc0Y2d3RGtnQllKaXhaODkza2NtaWdQOEtSNlJXQ1RnajJ6eHp0MU5RajRlX3JNWW5nZmFZUW4zcnh1a0dGUDV4TUN1R09kMURlMXNxbmtPRXFFeTB0Z0F3T1I4bkhIVkV1cHA5WmFSSFNWWTJndWExcVBwMVdraDBhWUppbi1oZDAtWDZ1aFRvNUtHdGVlLWRjVlg0WHNXT3lrTGgwN0Fxbm9WdnJlSHZabmNhcUdMUmV1SWxheV9fNzRBNWNPaFNfSzdkb1l3SGFGd3NrcHdjVVAtY1hlSC1iMGRBd09YUmJGSk50X1RZWFowRU1WVzZzU1p4c0J3eUxZMF9LSlVKb1VJeXZMblNOTVp5Ukl5S1JUZmhHQS0zWnZQNW41cWpIYkJndXR6R0YxYmlPNFZVUFMzMnk2TkVOdVo1YURncHQwRjA0V0twcGVBZGhaY1F1ajdFM3BsT0dTWkdpVUtobUJ2ZGJxOVVfcWRQZE5zZTVwZ1Qza0JLc01fdW0xcm53d0hDVVh4ZXY4VEJJemtkMXFaOGJFQmxWMkhHMjJ0RU1kNk51V1JUb2ljYUpyMHZJUjg3VkYtbU9Va1NLTnM2REtwTl9seDZUOFZvNmd4bE1VV2NxZjgzcXBtWGRzeFZSZWdOOWlkeloyQmladGhGXzdqbXJCejlISzZNRnVpdEJsQ29lRW5TR3ZmdjYtdHNQMWo0dVpkd3ZyVDhwbkVUQmxJYmRrMl81TzBROUs5N1Y1U3FDYW5xdkJRWGZ3Mkh0dGhMbjlGQjZOaHZIVU1GYXdQZXlYMHJ6bVZabWExSlFCVQ==",
                        "email":"chris@virtualelephant.com"
                },
                "registry.redhat.io":{
                        "auth":"fHVoYy1wb29sLTU3MGJiY2E2LTMyMjQtNDg0Ni04NzEwLTUxOGExMWVkOWI0ZDpleUpoYkdjaU9pSlNVelV4TWlKOS5leUp6ZFdJaU9pSXpNekEwT0dRMk5EQmtaalkwTWpoaE9XTmpOVGhqTkdWaE9EQTVOMlJtTUNKOS53d2ZjNzctS3J4dUUzMktHS1NKNGtldUtjWWZXMGRRX0VzX252OHNyeldDenlaS2gycUhtTEMzZjdUeUxSUm5leW0teDdZWHc0Y2d3RGtnQllKaXhaODkza2NtaWdQOEtSNlJXQ1RnajJ6eHp0MU5RajRlX3JNWW5nZmFZUW4zcnh1a0dGUDV4TUN1R09kMURlMXNxbmtPRXFFeTB0Z0F3T1I4bkhIVkV1cHA5WmFSSFNWWTJndWExcVBwMVdraDBhWUppbi1oZDAtWDZ1aFRvNUtHdGVlLWRjVlg0WHNXT3lrTGgwN0Fxbm9WdnJlSHZabmNhcUdMUmV1SWxheV9fNzRBNWNPaFNfSzdkb1l3SGFGd3NrcHdjVVAtY1hlSC1iMGRBd09YUmJGSk50X1RZWFowRU1WVzZzU1p4c0J3eUxZMF9LSlVKb1VJeXZMblNOTVp5Ukl5S1JUZmhHQS0zWnZQNW41cWpIYkJndXR6R0YxYmlPNFZVUFMzMnk2TkVOdVo1YURncHQwRjA0V0twcGVBZGhaY1F1ajdFM3BsT0dTWkdpVUtobUJ2ZGJxOVVfcWRQZE5zZTVwZ1Qza0JLc01fdW0xcm53d0hDVVh4ZXY4VEJJemtkMXFaOGJFQmxWMkhHMjJ0RU1kNk51V1JUb2ljYUpyMHZJUjg3VkYtbU9Va1NLTnM2REtwTl9seDZUOFZvNmd4bE1VV2NxZjgzcXBtWGRzeFZSZWdOOWlkeloyQmladGhGXzdqbXJCejlISzZNRnVpdEJsQ29lRW5TR3ZmdjYtdHNQMWo0dVpkd3ZyVDhwbkVUQmxJYmRrMl81TzBROUs5N1Y1U3FDYW5xdkJRWGZ3Mkh0dGhMbjlGQjZOaHZIVU1GYXdQZXlYMHJ6bVZabWExSlFCVQ==",
                        "email":"chris@virtualelephant.com"}
        }
}
```

```bash
echo -n '<username>:<password>' | base64
```

Copy the base64 password in the pull-secret.json file

```bash
oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=pull-secret.json
```