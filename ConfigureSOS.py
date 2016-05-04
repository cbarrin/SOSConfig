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
subprocess.call("sudo service iptables save", shell=True)

# STEP 2: Deleting queueing systems

# STEP 3: Configure any network parameters
print("CONFIGURING TCP PARAMETERS")

subprocess.call("sudo bash << EOF")

print("Setting parameters in /proc/sys/net/ipv4/..")
subprocess.call("echo 'htcp' > /proc/sys/net/ipv4/tcp_congestion_control")
subprocess.call("echo 1 > /proc/sys/net/ipv4/tcp_low_latency")
subprocess.call("echo '16777216 16777216 16777216' > /proc/sys/net/ipv4/tcp_mem")
subprocess.call("echo '4096 87380 16777216' > /proc/sys/net/ipv4/tcp_rmem")
subprocess.call("echo 0 > /proc/sys/net/ipv4/tcp_tcp_sack")
subprocess.call("echo 0 > /proc/sys/net/ipv4/tcp_timestamps")
subprocess.call("echo '4096 65536 16777216' > /proc/sys/net/ipv4/tcp_wmem")

print("Setting parameters in /proc/sys/net/core/..")
subprocess.call("echo 30000 > /proc/sys/net/core/netdev_max_backlog")
subprocess.call("echo 16777216 > /proc/sys/net/core/optmem_max")
subprocess.call("echo 16777216 > /proc/sys/net/core/rmem_default")
subprocess.call("echo 16777216 > /proc/sys/net/core/rmem_max")
subprocess.call("echo 16777216 > /proc/sys/net/core/wmem_default")
subprocess.call("echo 16777216 > /proc/sys/net/core/wmem_max")

print("Reloading sysctl now..")
subprocess.call("sysctl -p")

subprocess.call("EOF")

# STEP 4: Pin any interrupts to core 0

# STEP 5: Install and configure OVS

# STEP 6: Install and configure SOS agent
