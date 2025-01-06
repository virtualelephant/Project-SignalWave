# Assumes you have a working VCF environment and a VM template to clone

$vcServer = "vcenter-vcf01.home.virtualelephant.com"
$vcUsername = "administrator@vsphere.local"
$vcPassword = ""

Connect-VIServer -Server $vcServer -User $vcUsername -Password $vcPassword
# Variables
$templateName = "centos-stream-k8s-dhcp"
$destinationFolder = "Cilium AZ1"
$datastore = "Synology"  # Replace with your datastore
$cluster = "ve-m01-cluster-001"      # Replace with your cluster
$networkAdapterName = "Network adapter 1"
$newPortGroup = "ve-cilium-segment-az1"

$template = Get-VM -Name $templateName -ErrorAction Stop
$cluster = Get-Cluster -Name $clusterName -ErrorAction Stop
Write-Host "VM Template: $template"
Write-Host "Cluster: $cluster"


# Clone the template multiple times
1..3 | ForEach-Object {
    $vmName = "az1-cntrl-$($_)" # Define VM name dynamically
    New-VM -Name $vmName -VM $template -Datastore $datastore -Location $destinationFolder -ResourcePool $cluster
    $vm = Get-VM -Name $vmName
    $networkAdapter = Get-NetworkAdapter -VM $vm -Name $networkAdapterName
    Set-NetworkAdapter -NetworkAdapter $networkAdapter -NetworkName $newPortGroup -Confirm:$false
    Write-Host "Cloned VM: $vmName"
}

1..5 | ForEach-Object {
    $vmName = "az1-node-$($_)" # Define VM name dynamically
    New-VM -Name $vmName -VM $template -Datastore $datastore -Location $destinationFolder -ResourcePool $cluster
    $vm = Get-VM -Name $vmName
    $networkAdapter = Get-NetworkAdapter -VM $vm -Name $networkAdapterName
    Set-NetworkAdapter -NetworkAdapter $networkAdapter -NetworkName $newPortGroup -Confirm:$false
    Write-Host "Cloned VM: $vmName"
}

# Disconnect from vCenter
Disconnect-VIServer -Server $vcServer -Confirm:$false