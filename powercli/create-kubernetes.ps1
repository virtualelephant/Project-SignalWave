# Assumes you have a working VCF environment and a VM template to clone

$vcServer = "vcenter-vcf01.home.virtualelephant.com"
$vcUsername = "administrator@vsphere.local"
$vcPassword = "thAswU53n#CE2025!!"

Connect-VIServer -Server $vcServer -User $vcUsername -Password $vcPassword
# Variables
$prefix = "k8s-az2"
$templateName = "centos-stream-10-template"
$destinationFolder = "Kubernetes"
$datastore = "ve-m01-cluster-001-vsan"  # Replace with your datastore
$clusterName = "ve-m01-cluster-001"      # Replace with your cluster
$networkAdapterName = "Network adapter 1"
$newPortGroup = "az2-kubernetes"

# Control Plane VM Configuration
$ctrlCPU = 4
$ctrlMemoryGB = 8

# Worker Node VM Configuration
$nodeCPU = 8
$nodeMemoryGB = 16
$nodeDiskSizeGB = 250  # Desired size in GB

$template = Get-VM -Name $templateName -ErrorAction Stop
$cluster = Get-Cluster -Name $clusterName -ErrorAction Stop
Write-Host "VM Template: $template"
Write-Host "Cluster: $cluster"

# Clone the template multiple times
1..3 | ForEach-Object {
    $vmName = "$($prefix)-cntrl-0$($_)" # Define VM name dynamically
    if (Get-VM -Name $vmName -ErrorAction SilentlyContinue) {
        Write-Host "VM '$vmName' already exits. Skipping..."
        return
    }
    New-VM -Name $vmName -VM $template -Datastore $datastore -Location $destinationFolder -ResourcePool $cluster
    $vm = Get-VM -Name $vmName

    # Configure CPU and Memory values
    Set-VM -VM $vm -NumCpu $ctrlCPU -MemoryGB $ctrlMemoryGB -Confirm:$false

    # Configure Network
    $networkAdapter = Get-NetworkAdapter -VM $vm -Name $networkAdapterName
    Set-NetworkAdapter -NetworkAdapter $networkAdapter -Portgroup $newPortGroup -Confirm:$false
    
    # Set disk.EnableUUID = TRUE
    New-AdvancedSetting -Entity $vm -Name "disk.EnableUUID" -Value "TRUE" -Confirm:$false
    Write-Host "Cloned VM: $vmName"
}

1..5 | ForEach-Object {
    $vmName = "$($prefix)-node-0$($_)" # Define VM name dynamically
    if (Get-VM -Name $vmName -ErrorAction SilentlyContinue) {
        Write-Host "VM '$vmName' already exits. Skipping..."
        return
    }
    New-VM -Name $vmName -VM $template -Datastore $datastore -Location $destinationFolder -ResourcePool $cluster
    $vm = Get-VM -Name $vmName

    # Configure CPU and Memory Values
    Set-VM -VM $vm -NumCpu $nodeCPU -MemoryGB $nodeMemoryGB -Confirm:$false

    $networkAdapter = Get-NetworkAdapter -VM $vm -Name $networkAdapterName
    Set-NetworkAdapter -NetworkAdapter $networkAdapter -Portgroup $newPortGroup -Confirm:$false

    # Expand hard disk
    $hardDisk = Get-HardDisk -VM $vm | Where-Object { $_.Name -eq "Hard disk 1" }
    if ($hardDisk.CapacityGB -lt $nodeDiskSizeGB) {
        Set-HardDisk -HardDisk $hardDisk -CapacityGB $nodeDiskSizeGB -Confirm:$false
        Write-Host "Expanded disk for VM: $vmName to $nodeDiskSizeGB GB"
    }    
    # Set disk.EnableUUID = TRUE
    New-AdvancedSetting -Entity $vm -Name "disk.EnableUUID" -Value "TRUE" -Confirm:$false
    Write-Host "Cloned VM: $vmName"
}
# Disconnect from vCenter
Disconnect-VIServer -Server $vcServer -Confirm:$false