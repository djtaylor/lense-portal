#!/bin/bash
#
# Manager script for accessing the Python worker installation script.

# Create a temporary working directory
mkdir -p tmp

# Make the worker script executable
chmod +x worker.py

# Deploy local files and configure the environment
./worker.py "deploy"

# Reload the environment
source /etc/profile
ldconfig

# Run the main installation step[
./worker.py "install"