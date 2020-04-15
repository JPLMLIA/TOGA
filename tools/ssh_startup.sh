#!/bin/bash

# Tunnels from root to each node
for node in `pbsnodes -a -F dsv | awk -F"|" '{gsub("Name=","",$1); print $1 }'`; do ssh -R $node:9119:localhost:9119 gattaca -f -N -q; done