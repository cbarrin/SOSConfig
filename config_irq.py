import multiprocessing
import subprocess
import re
import sys

subprocess.call("sudo service irqbalance stop", shell=True)
subprocess.call("sudo service irqbalance status", shell=True)

num_cpus = multiprocessing.cpu_count()
interface = raw_input("What interface do you want to use? >> ")

if sys.version_info[:2] == (2, 6):
    interrupt_output = subprocess.Popen("cat /proc/interrupts | grep " + interface, shell=True, stdout=subprocess.PIPE)
    interrupt_output = interrupt_output.communicate()[0]

else:
    interrupt_output = subprocess.check_output("cat /proc/interrupts | grep " + interface, shell=True)

interrupt_output = interrupt_output.split('\n')

for index, interrupt in enumerate(interrupt_output):
    if interrupt:
        f = open("/proc/irq/" + re.sub("\D", "", interrupt.split()[0]) + "/smp_affinity_list", "r+")
        if index + 1 < num_cpus:
            f.write(str(index + 1))
        else:
            f.write(str(1) + "-" + str(num_cpus-1))
        print interrupt.split()[-1] + " now has affinity " + f.read()


