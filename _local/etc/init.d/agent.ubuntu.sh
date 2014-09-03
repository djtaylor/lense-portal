#!/bin/bash
source /etc/profile

# CloudScape Agent
#
# This is a server designed to handle system polling for a managed CloudScape
# host. Typically used to submit periodic reports of system data.

### BEGIN INIT INFO
#
# Provides:          cloudscape-agent
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: CloudScape Agent
# Description :      Service designed to submit polling data to the API server
#
### END INIT INFO

# Run the agent handler
python /usr/bin/cloudscape-agent "$@"