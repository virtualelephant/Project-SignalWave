# Assumes you have a working VCF environment and a VM template to clone

$vcServer = "VCENTER-FQDN"
$vcUsername = "USERNAME"
$vcPassword = "PASSWORD"

Connect-VIServer -Server $vcServer -User $vcUsername -Password $vcPassword
# Variables
$templateName = "TEMPLATE-NAME"
$destinationFolder = "VM-FOLDER-NAME"
$datastore = "DATASTORE-NAME"  # Replace with your datastore
$cluster = "CLUSTER-or-RESOURCE-POOL-NAME"      # Replace with your cluster
$networkAdapterName = "Network adapter 1"
$newPortGroup = "PORTGROUP-NAME"

$template = Get-VM -Name $templateName -ErrorAction Stop
$cluster = Get-Cluster -Name $clusterName -ErrorAction Stop
Write-Host "VM Template: $template"
Write-Host "Cluster: $cluster"

# Clone the template multiple times
1..3 | ForEach-Object {
    $vmName = "os-k8s-cntrl-$($_)" # Define VM name dynamically
    if (Get-VM -Name $vmName -ErrorAction SilentlyContinue) {
        Write-Host "VM '$vmName' already exits. Skipping..."
        return
    }
    New-VM -Name $vmName -VM $template -Datastore $datastore -Location $destinationFolder -ResourcePool $cluster
    $vm = Get-VM -Name $vmName
    $networkAdapter = Get-NetworkAdapter -VM $vm -Name $networkAdapterName
    Set-NetworkAdapter -NetworkAdapter $networkAdapter -NetworkName $newPortGroup -Confirm:$false
    # Set disk.EnableUUID = TRUE
    New-AdvancedSetting -Entity $vm -Name "disk.EnableUUID" -Value "TRUE" -Confirm:$false
    Write-Host "Cloned VM: $vmName"
}

1..5 | ForEach-Object {
    $vmName = "os-k8s-node-$($_)" # Define VM name dynamically
    if (Get-VM -Name $vmName -ErrorAction SilentlyContinue) {
        Write-Host "VM '$vmName' already exits. Skipping..."
        return
    }
    New-VM -Name $vmName -VM $template -Datastore $datastore -Location $destinationFolder -ResourcePool $cluster
    $vm = Get-VM -Name $vmName
    $networkAdapter = Get-NetworkAdapter -VM $vm -Name $networkAdapterName
    Set-NetworkAdapter -NetworkAdapter $networkAdapter -NetworkName $newPortGroup -Confirm:$false
    # Set disk.EnableUUID = TRUE
    New-AdvancedSetting -Entity $vm -Name "disk.EnableUUID" -Value "TRUE" -Confirm:$false
    Write-Host "Cloned VM: $vmName"
}
# Disconnect from vCenter
Disconnect-VIServer -Server $vcServer -Confirm:$false