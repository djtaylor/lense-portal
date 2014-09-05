#!/bin/bash

# Configuration directory
CONFIG_DIR=""

# Supported releases (Ubuntu/Debian)
declare -a RELEASES=("precise" "quantal" "raring" "saucy" "trusty" "wheezy")

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
		
		# Deploy for each supported release
		for RELEASE in ${RELEASES[@]}; do
			reprepro --confdir $CONFIG_DIR includedeb $RELEASE $PKG
		done
	done
}

# Configure and deploy
configure
deploy