#!/bin/bash
#
# Manager script for accessing the Python worker installation script.

# Current / installation locations
C_LOCATION=$(pwd)
I_LOCATION=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Change to the installation directory
cd $I_LOCATION

# Create a temporary working directory
mkdir -p tmp

# Deploy local files and configure the environment
./worker.py "deploy"
if [ $(echo $?) != 0 ]; then
	exit $?
fi

# Reload the environment and static library paths
source /etc/profile && ldconfig

# Run the main installation step
./worker.py "install"
if [ $(echo $?) != 0 ]; then
	exit $?
fi

# Return the the initial directory
cd $C_LOCATION