CloudScape
=========
CloudScape is a host management and software deployment system. It is based on the [Django] web framework, and contains the following key components:

----------------------
### CloudScape Engine ###
----------------------
This component is the API backbone of CloudScape. It handles saving and retrieving information from the database, and also takes care of all API calls made by the other components.

----------------------
### CloudScape Portal ###
----------------------
This component is the web front-end for CloudScape. It uses a combination of a server-side Python client and a client-side Socket.IO client to retrieve and update information from the engine component. All data retrieval and updates are done using API calls.

----------------------
### CloudScape Socket ###
----------------------
This component is a Socket.IO proxy server used to handle API calls from the portal client-side Socket.IO library. The socket proxy requires the availability of Node.JS as well as Socket.IO.

----------------------
### CloudScape Scheduler ###
----------------------
This component runs scheduled tasks for database and API maintenace, such as rebuilding search indexes, monitoring managed hosts, and caching data.

----------------------
### CloudScape Agent ###
----------------------
This component is installed on managed hosts, and runs as a server. It keeps track of system information, collects polling data, and manages software deployment. It uses a Python client to connect to the API cluster, to retrieve and update host information.

[Django]:https://www.djangoproject.com/