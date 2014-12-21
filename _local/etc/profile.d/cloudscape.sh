# CloudScape Environment
# 
# Shell script that sets up global environment variables. If you want to change
# the installation location of CloudScape, you should adjust the CLOUDSCAPE_BASE
# value in this file.

# CloudScape Base Directory
export CLOUDSCAPE_BASE="/opt/cloudscape"

# CloudScape Python Path
export PYTHONPATH="$CLOUDSCAPE_BASE/python"

# CloudScape Static Libraries
if [ ! -z $LD_LIBRARY_PATH ]; then
	export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$CLOUDSCAPE_BASE/python/lib"
else
	export LD_LIBRARY_PATH="$CLOUDSCAPE_BASE/python/lib"
fi