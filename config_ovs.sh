#!/bin/bash
#EDIT THIS BEFORE USE!!!!
CONTROLLER_IP=130.127.38.2
CONTROLLER_PORT=6011
DESIRED_IP=192.168.1.1/24
VLAN_INTERFACE=eth1


echo 'Building Bridge...'
sudo ovs-vsctl add-br br0
VLAN=$(ifconfig | awk '{print $1}' | grep "vlan")
sudo ovs-vsctl add-port br0 $VLAN
sudo ifconfig $VLAN 0 up
sudo ifconfig br0 $DESIRED_IP up
sudo ovs-vsctl set-controller br0 tcp:$CONTROLLER_IP:$CONTROLLER_PORT
sudo ovs-vsctl show
sudo ifconfig br0 mtu 8974
sudo ifconfig $VLAN_INTERFACE mtu 8974
sudo ifconfig $VLAN mtu 8974
ifconfig br0
