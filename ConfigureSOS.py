# This is the main configuration file for setting up SOS.
# It will be responsible for doing a few things:
#       - Deleting firewall rules
#       - Deleting any queueing system
#       - Configuring all the network parameters
#       - Pinning all of the interrupts
#       - Installing and configuring OVS
#       - Installing and configure the SOS agent
import subprocess

# STEP 1: Deleting firewall rules

# STEP 2: Deleting queueing systems

# STEP 3: Configure any network parameters

# STEP 4: Pin any interrupts to core 0

# STEP 5: Install and configure OVS
## Setting variables
## Not setting MTU, will the # of interfaces remain same? such as CloudLab has 2 (physical and VLAN).

controllerIP = raw_input("Please enter controller IP >>")
controllerPort = raw_input("Please enter controller Port >>")
hostInterface = raw_input("Please enter the local interface name>>")
hostIP = raw_input("Please enter Host IP>>")

print "Building bridge..."
subprocess.call("sudo ovs-vsctl add-br br0", shell=True)
subprocess.call("sudo ovs-vsctl add-port br0 " + hostInterface, shell=True)
subprocess.call("sudo ifconfig " + hostInterface + " 0 up", shell=True)
subprocess.call("sudo ifconfig br0 " + hostIP + " up", shell=True)
subprocess.call("sudo ovs-vsctl set-controller br0 tcp:" + controllerIP + ":" + controllerPort, shell=True)
print subprocess.check_output("sudo ovs-vsctl show", shell=True)
print subprocess.check_output("ifconfig br0", shell=True)

# STEP 6: Install and configure SOS agent
