#!/bin/bash
echo 'Checking and installing necessary dependencies...'
sudo apt-get update
cg=$(sudo apt --installed list | grep "clang")
uu=$(sudo apt --installed list | grep "uuid-dev")
lx=$(sudo apt --installed list | grep "libxml2-dev")
if [ -z $cg ] || [ -z $uu ] || [-z $lx ];
then
	sudo apt-get install clang -y
	sudo apt-get install uuid-dev -y
	sudo apt-get install libxml2-dev -y
else
	echo 'Dependency install complete, 5 second rest to exit should errors occur.'
	sleep 5
fi

echo 'Installing SoS Agents now...'
sudo git clone http://github.com/cbarrin/sos-agent 
cd ./sos-agent

sudo make 
echo 'Instillation complete.'
echo 'To run the SoS agent run ./run.sh.'
echo 'Recommended that you do so from a screen session.'
