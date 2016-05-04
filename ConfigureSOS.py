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
print("DELETING FIREWALL RULES")

print("Flushing iptables rules.")
subprocess.call("sudo iptables --flush", shell=True)

print("Saving flushed iptables to file. Changes will be saved if service is restarted.")
subprocess.call("sudo service iptables saves", shell=True)

# STEP 2: Deleting queueing systems

# STEP 3: Configure any network parameters

# STEP 4: Pin any interrupts to core 0

# STEP 5: Install and configure OVS

# STEP 6: Install and configure SOS agent
