#!/bin/bash

echo " * Creating a swap file in /swapfile..."
fallocate -l 1024M /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Set the swap as permanent settings.
echo "/swapfile   none    swap    defaults    0   0" >> /etc/fstab

echo " * Setting the swappiness..."
# Lower the swappiness.
sysctl vm.swappiness=5
# And make it the default settings.
echo "vm.swappiness=5" >> /etc/sysctl.conf

echo " * Swapfile active"
