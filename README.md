Project Cloudscape Overview
=========

----------------------
### Current State of Project Cloudscape ###
----------------------

  The code itself is in good condition, but documentation is terrible (basically non-existent). Most of the files have adequate commenting to make sense, but a layout of the overall structure and architecture is lacking.
  Good luck trying to get it installed. I’ve made a few efforts, but for now its the painful process of fixing module and package dependencies to get it to work. On a fresh system it can prove to be tedious.
  Hopefully my code is at least entertaining to read (for good or bad reasons).

----------------------
### Project Cloudscape Overview ###
----------------------

  In the grand scheme of things, I suppose I would like to see Cloudscape become a user driven cloud platform, providing access to a high quality IT infrastructure, with an emphasis on HCI principles and flexibility. Originally this started as a management platform for both cloud and physical IT assets, but as my views on IT have changed a lot in the past year, so has my view on Cloudscape. I’m going to start by breaking it down into two separate components.

----------------------
### Cloudscape Nexus ###
----------------------

	Nexus will be the API engine and proxy server from the original Cloudscape project. I want Nexus to be highly configurable and intuitive to use. I want a user to be able to construct an API system from modular components, via a drag and drop style web interface. User APIs can be saved and ported to other systems, and used in almost any application.
  This is definitely the focus of attention for now. I suppose it could be classed as “API as a Service”. Don’t know if that exists yet (I’ll research it later). 

----------------------
### Cloudscape Datacenter ###
----------------------

	Datacenter will be consist of a Nexus configuration, a user interface, as well as a collection of agent software. Most likely Datacenter will be broken into further subsections.

----------------------
### Challenges ###
----------------------

* Documentation. This is first and foremost. I need to document what I have done so far.
* Making utility processing modular. Right now I feel like you will simply have to have enough options in the user interface to create what is needed, so the utility handler can easily be ported to other systems
* Making a configuration UI for Nexus. Mainly because it is time consuming and my poor familiarity with advanced web UIs.
* Handling security properly. As this is my first major project, I am by no means an expert in securing API communications and proper protocol. This will definitely need improvement.
