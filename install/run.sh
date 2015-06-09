#!/bin/bash

# Check if '.cloudscaperc' is being sourced
if [ -z "$(cat ~/.bashrc | grep 'source ~/.cloudscaperc')" ]; then
	echo "source ~/.cloudscaperc" >> ~/.bashrc
fi

# Check if a user-defined server configuration exists
if [ ! -f ~/conf/server.conf ]; then
	cp -a ~/conf/default/server.conf ~/conf/server.conf
fi 

# Create the log and run directories
mkdir -p ~/log ~/run

exit 0