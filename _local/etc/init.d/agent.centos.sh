#!/bin/bash
source /etc/profile

# CloudScape Agent
#
# This is a server designed to handle system polling for a managed CloudScape
# host. Typically used to submit periodic reports of system data.

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
# Init Info \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
#
# Provides:          cloudscape-agent
# Default-Start:     3 4 5
# Short-Description: CloudScape Agent
# Description:       Service designed to submit polling data to the API server

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
# Chkconfig Info \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
#
# cloudscape-agent:  CloudScape Agent
# chkconfig:         345 97 03
# description:       Service designed to submit polling data to the API server
# processname:       cloudscape-agent
# pidfile:           /opt/clousdscape/run/cloudscape-agent.pid

# Run the agent handler
python /usr/bin/cloudscape-agent "$@"