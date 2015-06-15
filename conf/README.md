Server Configuration
=========
You should place your modified 'server.conf' file in this directory. You can create a copy from the 'docs/examples/server.conf' file and make any appropriate changes for your environment.

Default Configuration
---------
The file 'server.conf' found in the 'default' directory contains a configuration file with default configuration settings. Any directives found in the user's 'server.conf' file will override values found in this file. See the file 'default/server.conf' for all configuration options.

Apache Configuration
---------
The directory 'apache' contains virtual host configuration files that allow both the engine and portal to work. Apache2 must be installed, as well as 'mod_wsgi'. You must either move these files to 'sites-available' and enable them, or update 'apache2.conf' to point to 'conf/apache' for enabled virtual hosts. You will also need to update 'ports.conf' (on Ubuntu systems) and enable whichever port you choose for the API engine (default is 10550).