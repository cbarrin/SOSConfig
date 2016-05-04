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

interface = raw_input("Which interface to delete the queues?? >>")
subprocess.call("sudo tc qdisc del dev " + interface + " root", shell=True)
subprocess.call("sudo tc -s qdisc ls dev " + interface, shell=True)

# STEP 3: Configure any network parameters

# STEP 4: Pin any interrupts to core 0

# STEP 5: Install and configure OVS

# STEP 6: Install and configure SOS agent
