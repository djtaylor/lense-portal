#!/bin/bash
#
# Manager script for accessing the Python worker installation script.

# Get the location of the installation manager
LOCATION=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo "LOCATION: $LOCATION"

# Create a temporary working directory
mkdir -p tmp

# Deploy local files and configure the environment
./worker.py "deploy"

# Reload the environment
source /etc/profile
ldconfig

# Run the main installation step[
./worker.py "install"