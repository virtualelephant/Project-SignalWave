# Assumes you have a working VCF environment and a VM template to clone

$vcServer = "vcenter-vcf01.home.virtualelephant.com"
$vcUsername = "administrator@vsphere.local"
$vcPassword = "thAswU53n#CE2025!!"

Connect-VIServer -Server $vcServer -User $vcUsername -Password $vcPassword
# Variables
$templateName = "centos-stream-dhcp"
$destinationFolder = "Cilium"
$datastore = "Synology"  # Replace with your datastore
$cluster = "ve-m01-cluster-001"      # Replace with your cluster

$template = Get-VM -Name $templateName -ErrorAction Stop
$cluster = Get-Cluster -Name $clusterName -ErrorAction Stop
Write-Host "VM Template: $template"
Write-Host "Cluster: $cluster"


# Clone the template multiple times
1..3 | ForEach-Object {
    $vmName = "az1-cntrl-$($_)" # Define VM name dynamically
    New-VM -Name $vmName -VM $template -Datastore $datastore -Location $destinationFolder -ResourcePool $cluster
    Write-Host "Cloned VM: $vmName"
}

1..5 | ForEach-Object {
    $vmName = "az1-node-$($_)" # Define VM name dynamically
    New-VM -Name $vmName -VM $template -Datastore $datastore -Location $destinationFolder -ResourcePool $cluster
    Write-Host "Cloned VM: $vmName"
}

# Disconnect from vCenter
Disconnect-VIServer -Server $vcServer -Confirm:$false