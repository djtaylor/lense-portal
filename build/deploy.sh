#!/bin/bash
#
# Helper script used to deploy *.deb packages generated with 'build.py' to a repository
# on the local system. This assumes you are running a repository server on the same
# machine you are building the packages on. This script requires you have 'reprepro'
# installed and the appropriate files, mainly 'distributions' and 'options' in the 'conf'
# directory of your repository root.

# Configuration directory
CONFDIR=""

# Supported releases (Ubuntu/Debian)
declare -a RELEASES=("precise" "quantal" "raring" "saucy" "trusty" "wheezy")

# Configure deployment
configure() {
	
	# Get configuration directory
	get_confdir() {
		echo -ne "Please enter your repository configuration directory: " && read CONFDIR
		[ -z $CONFDIR ] && get_confdir
		if [ ! -d $CONFDIR ]; then
			echo -e "ERROR: Directory '$CONFDIR' not found"
			get_conf_dir
		fi
	}
	get_confdir
}

# Deploy packages
deploy() {
	
	# Deploy each package
	for PKG in $(find output/*.deb -type f); do
		
		# Deploy for each supported release
		for RELEASE in ${RELEASES[@]}; do
			reprepro --confdir $CONFDIR includedeb $RELEASE $PKG
		done
	done
}

# Configure and deploy
configure
deploy