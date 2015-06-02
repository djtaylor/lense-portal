#!/bin/bash
#
# Manager script for accessing the Python worker installation script.

worker() {
	./worker "$1"
	if [ $(echo $?) != 0]; then
		exit $?
	fi 	
}

# Current / installation locations
C_LOCATION=$(pwd)
I_LOCATION=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Change to the installation directory
cd $I_LOCATION

# Create a temporary working directory
mkdir -p tmp

# Deploy local files and configure the environment
worker "deploy"

# Reload the environment and static library paths
source /etc/profile && ldconfig

# Run the main installation step
worker "install"

# Return the the initial directory
cd $C_LOCATION