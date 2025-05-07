# Caveats for running Project SignalWave in Red Hat OpenShift
Red Hat OpenShift is very opinionated around how certian things should be done within the environment. For instance, NFS is not allowed as a CSI, so leveraging the typical NFS external provisioner is not an option within Red Hat OpenShift without significant modification to the security policies.

## Configuring LDAP for Authentication

```yaml
identityProviders:
- name: ldap_provider
  mappingMethod: claim
  type: LDAP
  ldap:
    url: "ldap://ldap01.home.virtualelephant.com:389/ou=People,dc=home,dc=virtualelephant,dc=com?uid"
    bindDN: "uid=k8s-service,ou=People,dc=home,dc=virtualelephant,dc=com"
    bindPassword:
      name: ldap-bind-secret
    insecure: true
    attributes:
      id: ["uid"]
      email: ["mail"]
      name: ["cn"]
      preferredUsername: ["uid"]
```

Additional steps are required after adding the authentication source in the GUI or through the CLI.

```bash
oc create secret generic ldap-bind-secret \
  --namespace=openshift-config \
  --from-literal=bindPassword='your_k8s-service_password'
```

You can verify the OAuth Provider afterwards with the following check:

```bash
oc get oauth cluster -o yaml
```

Next we want to either grant permissions to a single user or to a group of users:

```bash
oc adm policy add-cluster-role-to-user cluster-admin devops-user1
```

To add a group of users, you need to sync the LDAP Groups with RHOS.

First, create a groupsync.yaml file with your specific information in it:

```yaml
apiVersion: v1
kind: LDAPSyncConfig
url: "ldap://ldap01.home.virtualelephant.com:389"
bindDN: "uid=k8s-service,ou=People,dc=home,dc=virtualelephant,dc=com"
bindPassword:
  file: "/home/deploy/ldap-config/bindPassword"
insecure: true
rfc2307:
  groupsQuery:
    baseDN: "ou=Groups,dc=home,dc=virtualelephant,dc=com"
    scope: sub
    derefAliases: never
    filter: "(objectClass=groupOfNames)"
  groupUIDAttribute: "dn"
  groupNameAttributes:
    - cn
  groupMembershipAttributes:
    - member
  usersQuery:
    baseDN: "ou=People,dc=home,dc=virtualelephant,dc=com"
    scope: sub
    derefAliases: never
  userUIDAttribute: "dn"
  userNameAttributes:
    - uid
groupUIDNameMapping:
  "cn=devops-team,ou=Groups,dc=home,dc=virtualelephant,dc=com": "devops-team"
 ```

You need to create the `bindPassword` file before syncing the LDAP group:

```bash
echo 'your_k8s_service_password' | sudo tee /home/deploy/ldap-config/bindPassword > /dev/null
chmod 644 /home/deploy/ldap-config/bindPassword
tr -d '\n' < /home/deploy/ldap-config/bindPassword > temp && mv temp /home/deploy/ldap-config/bindPassword
```

 Once you have created the `groupsync.yaml` file, you can sync RHOS:

 ```bash
 oc adm groups sync \
  --sync-config=groupsync.yaml \
  --confirm
```

Verify the group was created:

```bash
oc get group devops-team -o yaml
```

Assign the group Cluster-wide Access:

```bash
oc adm policy add-cluster-role-to-group cluster-admin devops-team
```

Or assign the group Namespace-specific Access:

```bash
oc adm policy add-role-to-group edit devops-team -n devops-project
```

---

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