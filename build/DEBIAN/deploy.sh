#!/bin/bash

# Configuration directory
CONFIG_DIR=""

# Configure deployment
configure() {
	
	# Get configuration directory
	get_conf_dir() {
		echo -ne "Please enter your repository configuration directory: " && read CONFIG_DIR
		[ -z $CONFIG_DIR ] && get_conf_dir
		if [ ! -d $CONFIG_DIR ]; then
			echo -e "ERROR: Directory '$CONFIG_DIR' not found"
			get_conf_dir
		fi
	}
	get_conf_dir
}

# Deploy packages
deploy() {
	
	# Deploy each package
	for PKG in $(find output/*.deb -type f); do
		reprepro --confdir $CONFIG_DIR includedeb trusty $PKG
	done
}

# Configure and deploy
configure
deploy