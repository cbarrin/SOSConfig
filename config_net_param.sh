#!/bin/bash
sudo bash << EOF

cd /proc/sys/net/
echo 0 > ipv4/tcp_timestamps
echo 0 > ipv4/tcp_sack
echo 16777216 > core/rmem_max
echo 16777216 > core/wmem_max
echo 16777216 > core/wmem_default
echo 16777216 > core/rmem_default
echo 16777216 > core/optmem_max
echo '16777216 16777216 16777216' > ipv4/tcp_mem
echo '4096 87380 16777216' > ipv4/tcp_rmem
echo '4096 65536 16777216' > ipv4/tcp_wmem
echo 1 > ipv4/tcp_low_latency
echo 30000 > core/netdev_max_backlog
echo 'htcp' > ipv4/tcp_congestion_control

sysctl -p
EOF
