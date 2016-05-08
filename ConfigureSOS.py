#!/usr/bin/python
# This is the main configuration file for setting up SOS.
# It will be responsible for doing a few things:
#       - Deleting firewall rules
#       - Deleting any queueing system
#       - Configuring all the network parameters
#       - Pinning all of the interrupts
#       - Installing and configuring OVS
#       - Installing and configure the SOS agent

import fileinput
import multiprocessing
import re
import subprocess
import sys


# Get the package manager.. yum for CentOS and apt-get for Ubuntu
def getPackageManager():
    r = subprocess.call("cat /etc/*-release | grep -c CentOS", shell=True)
    if r == 0:
        print("CentOS detected. Using yum as package manager..")
        return "yum"
    else:
        print("Using apt-get as package manager..")
        return "apt-get"


def deleteFirewallRules():
    print("\nDELETING FIREWALL RULES")

    print("Flushing iptables rules.")
    subprocess.call("sudo iptables --flush", shell=True)

    print("Saving flushed iptables to file. Changes will be saved if service is restarted.")
    subprocess.call("sudo service iptables save", shell=True)


def deleteQueueingSystems():
    ##We might have to extend this to iterate for every interface
    # TODO: Make UI more robust in this section

    interface = raw_input("Which interface to delete the queues?? >>")
    print "\nDeleting queues for interface", interface
    ret = subprocess.check_output("sudo tc -s qdisc ls dev " + interface, shell=True)
    if ret:
        subprocess.call("sudo tc qdisc del dev " + interface + " root", shell=True)
        # subprocess.call("sudo tc -s qdisc ls dev " + interface, shell=True)
        print "Queues deleted for interface", interface
    else:
        print "No queues found for interface", interface


def configureNetworkParameters():
    print("\nCONFIGURING TCP PARAMETERS")

    print("Setting parameters in /proc/sys/net/ipv4/..")
    subprocess.call("echo 'htcp' > /proc/sys/net/ipv4/tcp_congestion_control", shell=True)
    subprocess.call("echo 1 > /proc/sys/net/ipv4/tcp_low_latency", shell=True)
    subprocess.call("echo '16777216 16777216 16777216' > /proc/sys/net/ipv4/tcp_mem", shell=True)
    subprocess.call("echo '4096 87380 16777216' > /proc/sys/net/ipv4/tcp_rmem", shell=True)
    subprocess.call("echo 0 > /proc/sys/net/ipv4/tcp_sack", shell=True)
    subprocess.call("echo 0 > /proc/sys/net/ipv4/tcp_timestamps", shell=True)
    subprocess.call("echo '4096 65536 16777216' > /proc/sys/net/ipv4/tcp_wmem", shell=True)

    print("Setting parameters in /proc/sys/net/core/..")
    subprocess.call("echo 30000 > /proc/sys/net/core/netdev_max_backlog", shell=True)
    subprocess.call("echo 16777216 > /proc/sys/net/core/optmem_max", shell=True)
    subprocess.call("echo 16777216 > /proc/sys/net/core/rmem_default", shell=True)
    subprocess.call("echo 16777216 > /proc/sys/net/core/rmem_max", shell=True)
    subprocess.call("echo 16777216 > /proc/sys/net/core/wmem_default", shell=True)
    subprocess.call("echo 16777216 > /proc/sys/net/core/wmem_max", shell=True)


def pinInterrupts():
    print("PINNING INTERRUPTS")

    print("Stopping the irqbalance service..")
    subprocess.call("sudo service irqbalance stop", shell=True)
    subprocess.call("sudo service irqbalance status", shell=True)

    # TODO: Make it more obvious which is the right interface to choose. Clean up UI.
    while True:
        print("\nInterface:")
        subprocess.call("ifconfig -a | sed 's/[ \t].*//;/^\(lo\|\)$/d'", shell=True)
        print("\n")
        interface = raw_input("What interface do you want to pin? >> ")
        subprocess.call("ifconfig " + interface, shell=True)
        confirm = raw_input("Are you sure you want to pin interrupts for interface " + interface + "? >> ")
        confirm = confirm.strip().lower()
        if confirm == "yes" or confirm == "y":
            # TODO: Use 'ip link' to find vlans
            interface = interface.split('.')[0]
            break

    # TODO: Make sure this works for every version of python.
    if sys.version_info[:2] == (2, 6):
        print("Python v2.6 detected. Using Popen.")
        interrupt_output = subprocess.Popen("cat /proc/interrupts | grep " + interface, shell=True,
                                            stdout=subprocess.PIPE)
        interrupt_output = interrupt_output.communicate()[0]

    else:
        print("Python version greater than v2.6 detected. Using check_output.")
        interrupt_output = subprocess.check_output("cat /proc/interrupts | grep " + interface, shell=True)

    interrupt_output = interrupt_output.split('\n')

    num_cpus = multiprocessing.cpu_count()
    print("You have " + str(num_cpus) + " cpus!")

    print("Setting smp_affinity_list values in /proc/irq/ to spread interrupts across all cores except core 0.")
    for index, interrupt in enumerate(interrupt_output):
        if interrupt:
            f = open("/proc/irq/" + re.sub("\D", "", interrupt.split()[0]) + "/smp_affinity_list", "r+")
            if index + 1 < num_cpus:
                f.write(str(index + 1))
            else:
                f.write(str(1) + "-" + str(num_cpus - 1))
            print(interrupt.split()[-1] + " now has affinity " + f.read())

            # TODO: Push other interrupts to core 0.


def setMtu():
    while True:
        print("\nInterface:")
        subprocess.call("ip addr | grep mtu | awk '/mtu/{print $2,$4,$5}'", shell=True)
        print("\n")
        interface = raw_input("What interface do you want to set the mtu for? >> ")
        mtu = raw_input("And what do you want the mtu to be? >> ")
        try:
            subprocess.check_call("ip link set " + interface + " mtu " + mtu, shell=True)
            choice = raw_input("MTU set! Do you want to set another? >> ")
            choice = choice.strip().lower()
            if choice == "no" or choice == "n":
                break
        except(subprocess.CalledProcessError):
            choice = raw_input("Invalid value! Try again? >> ")
            choice = choice.strip().lower()
            if choice == "no" or choice == "n":
                break


def configureOVS():
    # We need to check if OVS is installed first. If it is not, then we should install it.

    try:
        subprocess.check_call("sudo ovs-vsctl show", shell=True)

    except(subprocess.CalledProcessError):
        # TODO: Install OVS.
        print("OVS is not installed! Install OVS and rerun the script. Exiting..")
        exit(1)

    controllerIP = raw_input("Please enter controller IP >> ")
    controllerPort = raw_input("Please enter controller OpenFlow port >> ")
    hostInterface = raw_input("Please enter the local interface name >> ")
    hostIP = raw_input("Please enter host IP >>")
    mtu = raw_input("Please enter the mtu for the local interface and the bridge >> ")

    print("Building bridge...")
    subprocess.call("sudo ovs-vsctl add-br br0", shell=True)
    subprocess.call("sudo ovs-vsctl add-port br0 " + hostInterface, shell=True)
    subprocess.call("sudo ifconfig " + hostInterface + " 0 up", shell=True)
    subprocess.call("sudo ifconfig br0 " + hostIP + " up", shell=True)
    subprocess.call("sudo ovs-vsctl set-controller br0 tcp:" + controllerIP + ":" + controllerPort, shell=True)
    subprocess.call("sudo ifconfig br0 mtu " + mtu, shell=True)
    subprocess.call("sudo ifconfig " + hostInterface + " mtu " + mtu, shell=True)
    subprocess.call("sudo ovs-vsctl show", shell=True)
    subprocess.call("ifconfig br0", shell=True)


def installAndConfigureAgent():
    print("\nInstalling and configuring the SOS agent!")

    print("Installing necessary dependencies!")
    pm = getPackageManager()
    print("Installing clang..")
    subprocess.call("sudo " + pm + " install clang -y")
    print("Installing uuid-dev..")
    subprocess.call("sudo " + pm + " install uuid-dev -y")
    print("Installing libxml2-dev..")
    subprocess.call("sudo " + pm + " install libxml2-dev -y")

    print("Installing the SOS agent..")
    subprocess.call("sudo git clone https://github.com/cbarrin/sos-agent.git", shell=True)

    subprocess.call("cd sos-agent", shell=True)

    # TODO: Make sure this works for every version of python.
    if sys.version_info[:2] == (2, 6):
        print("Python v2.6 detected. Using Popen.")
        agent_subnet = subprocess.Popen("ip -o addr show | grep -E 'br0.*inet ' | awk '//{print $6}'", shell=True,
                                        stdout=subprocess.PIPE)
        agent_subnet = agent_subnet.communicate()[0]

    else:
        print("Python version greater than v2.6 detected. Using check_output.")
        agent_subnet = subprocess.check_output("ip -o addr show | grep -E 'br0.*inet ' | awk '//{print $6}'",
                                               shell=True)

    # Replace DISCOVERY_DEST_ADDR and STATISTICS_DEST_ADDR with the subnet of 'br0'
    # Two assumptions are made: that the current subnet is '192.168.1.255' and that
    # the bridge is named 'br0'.
    with fileinput.FileInput('common.h', inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace('192.168.1.255', agent_subnet))

    # Not sure if this will work.. Might have to 'cd'
    subprocess.call("make", shell=True)

    print("To run the agent, use the command './run.sh'")


def configureEverything():
    # STEP 1: Deleting firewall rules
    deleteFirewallRules()
    # STEP 2: Deleting queueing systems
    deleteQueueingSystems()
    # STEP 3: Configure any network parameters
    configureNetworkParameters()
    # STEP 4: Pin any interrupts to core 0
    pinInterrupts()
    # STEP 5: Install and configure OVS
    configureOVS()
    # STEP 6: Install and configure SOS agent
    installAndConfigureAgent()


def quitProgram():
    exit(1)


options = {'0': configureEverything,
           '1': deleteFirewallRules,
           '2': deleteQueueingSystems,
           '3': configureNetworkParameters,
           '4': pinInterrupts,
           '5': setMtu,
           '6': configureOVS,
           '7': installAndConfigureAgent,
           '8': quitProgram
           }

while True:
    print("\nSOS CONFIGURATION!")
    print("0: Configure everything!")
    print("1: Delete firewall rules.")
    print("2: Delete queueing systems.")
    print("3: Configure network parameters.")
    print("4: Pin interrupts.")
    print("5: Set MTU.")
    print("6: Configure OVS.")
    print("7: Install and configure the SOS agent.")
    print("8: Quit")

    choice = raw_input("Choose a number to run a module. What do you want to do? >> ")

    try:
        options[choice]()
    except(KeyError):
        print("Invalid key pressed. Choose a number 0-8!")
