import os
import re
import sys
import json
import copy
import time
import base64
import shutil
import random
import string
import datetime
from uuid import uuid4
from threading import Thread

# Django Libraries
from django.conf import settings

# CloudScape Variables
from cloudscape.common.vars import F_RUNNING, F_ERROR, F_SERVICE, F_UTILITY, F_GROUP, \
                                   OS_SUPPORTED, L_BASE, W_BASE, A_EXECPKG, F_INSTALL, \
                                   F_UNINSTALL, F_MANAGED, F_UNMANAGED, A_LINUX, A_WINDOWS, \
                                   H_LINUX, H_WINDOWS, C_BASE, np

# CloudScape Libraries
from cloudscape.common import archive as archive
from cloudscape.common.remote import RemoteConnect
from cloudscape.common.utils import valid, invalid, obj_extract
from cloudscape.common.utils import JSONTemplate, FileSec
from cloudscape.engine.api.core.connect import HostConnect
from cloudscape.engine.api.core import host as host_utils
from cloudscape.engine.api.app.formula.models import DBFormulaDetails, DBFormulaTemplates, DBFormulaRegistry, DBFormulaEvents
from cloudscape.engine.api.app.host.models import DBHostDetails, DBHostFormulas, DBHostGroups, DBHostGroupMembers
from cloudscape.engine.api.util.formula.parse import FormulaParse

class FormulaEventWait:
    """
    This API class is used to wait for events that should be set using the
    'FormulaEventSet' utility. The host will make a blocking HTTP request to the
    API until either the timeout has been reached, or the event has been set in
    the database.
    
    Each event can contain a 'metadata' column in the database which stores a
    JSON encoded object. When the event is found to be set, the event metadata
    set by the event setter is returned to any nodes that were waiting.
    """
    def __init__(self, parent):
        """
        Initialize the formula event waiting utility.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        self.api           = parent
        
        # Event ID / Timeout
        self.event_id      = None
        self.event_timeout = None

    def launch(self):
        """
        Main method for waiting for formula events. Returns any event metadata
        found in the database.
        """
        
        # Formula event ID
        if not 'event_id' in self.api.data:
            return invalid('Must supploy a formula <event_id> parameter')
        self.event_id = self.api.data['event_id']

        # Make sure a timeout is specified
        if not 'event_timeout' in self.api.data:
            return invalid('Must supply a formula <event_timeout> parameter')
        self.event_timeout = int(self.api.data['event_timeout'])
    
        # Start the event waiter
        w_count = 0
        w_event = False
        while w_count <= self.event_timeout:
            w_count += 3
            
            # Look for the event
            if DBFormulaEvents.objects.filter(event_id=self.event_id).count():
                w_event = True
                e_meta  = json.loads(DBFormulaEvents.objects.filter(event_id=self.event_id).values()[0]['event_meta'])
                self.api.log.info('Formula event match: event_id=%s, event_meta=%s' % (self.event_id, e_meta))
                break
            time.sleep(3)
    
        # If the event was set before the timeout
        if w_event:
            return valid({'event_id': self.event_id, 'event_meta': e_meta})
        else:
            return invalid('Formula event timeout reached after %s seconds' % self.event_timeout)

class FormulaEventSet:
    """
    This API class is used to set formula events in the database. Formula events
    are used when running formula groups between clusters of nodes, and specific
    nodes must wait at certain points in their run cycle. For example:
    
    Deploying an HA MySQL cluster:
    
    1.) Master node begins to deploy
    2.) Secondary nodes begin to deploy, but cannot complete until master node does
    
    The secondary nodes will make a call to the 'FormulaEventWait' class and will continue
    waiting until a timeout has been reached or the event has been set by the master node.
    
    A node setting a formula event may optionally specify event metadata in JSON format
    that can be returned to any nodes waiting on this event.
    """
    def __init__(self, parent):
        """
        Initialize the formula event setter utility.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        self.api      = parent

        # Event ID
        self.event_id = None

    def launch(self):
        """
        Main method for setting formula events.
        """
        
        # Formula event ID
        if not 'event_id' in self.api.data:
            return invalid('Must supploy a formula <event_id> parameter')
        self.event_id = self.api.data['event_id']
        
        # Make sure the event ID is unique
        if DBFormulaEvents.objects.filter(event_id=self.event_id).count():
            return invalid('Formula event ID <%s> already set, must be unique to prevent conflicts' % self.event_id)
        
        # Set the event in the database
        try:
            e_meta  = '{}' if not ('event_meta' in self.api.data) else (json.dumps(self.api.data['event_meta']))
            f_event = DBFormulaEvents(event_id=self.event_id, event_meta=e_meta)
            f_event.save()
            self.api.log.info('Set formula event: event_id=%s, event_meta=%s' % (self.event_id, e_meta))
            return valid('Successfully set formula event \'%s\'' % self.event_id)
        except Exception as e:
            return invalid('Failed to set formula event \'%s\': %s' % (self.event_id, str(e)))
        
class FormulaVerify:
    """
    API class invoked when an agent attempts to run an encrypted package. Before
    running, the agent must generate a checksum of the package and submit to the
    API server. The following conditions must be met to verify and return the
    decryption key:
    
    1.) The checksum must match with the database. Each package is salted with a 
    random file to ensure unique checksums for every package.
    2.) The formula package must be registered to the host.
    3.) The formula package must have not already been verified or decrypted.
    
    If all the conditions are met, set the 'verified' flag to true and return the
    decryption key.
    """
    def __init__(self, parent):
        """
        Initialize the formula verification utility.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        self.api = parent
        
    # Launch the formula package verification process
    def launch(self):
        """
        Main method for the formula verification process.
        """
        required = ['host_uuid', 'pkg_uuid', 'checksum']
        for key in required:
            if not key in self.api.data:
                return invalid(self.api.log.error('Missing required key \'%s\' in request body' % key))
        self.pkg      = self.api.data['pkg_uuid']
        self.host     = self.api.data['host_uuid']
        self.checksum = self.api.data['checksum']

        # Log the verification attempt
        self.api.log.info('Host \'%s\' attempting verification of package \'%s\' with checksum \'%s\'' % (self.host, self.pkg, self.checksum))

        # Make sure the host exists
        if not DBHostDetails.objects.filter(uuid=self.host).count():
            return invalid(self.api.log.error('Failed to locate host \'%s\' in the database' % self.host))

        # Make sure the package is registered to the host
        if not DBFormulaRegistry.objects.filter(host=self.host).filter(uuid=self.pkg).count():
            return invalid(self.api.log.error('The requested package \'%s\' does not exist or is not registered to the host \'%s\'' % (self.pkg, self.host)))

        # Get the formula registration row
        fr_row = DBFormulaRegistry.objects.filter(host=self.host).filter(uuid=self.pkg).values()[0]
        
        # Make sure the checksum matches
        if not self.checksum == fr_row['checksum']:
            return invalid('The submitted package checksum does not match the registered checksum')
        self.api.log.info('Checksum verification for package \'%s\' succeeded' % self.pkg)
        
        # Make sure the package hasn't already been verified or decrypted
        if fr_row['verified'] or fr_row['decrypted']:
            return invalid(self.api.log.error('The requested pacakge \'%s\' has already been verified or decrypted' % self.pkg))
        
        # Everything looks good, update the database
        DBFormulaRegistry.objects.filter(host=self.host).filter(uuid=self.pkg).update(verified = True)
      
        # Get the encryption key
        self.api.socket.loading('Agent verified formula package...')
        self.api.log.info('Returning package decryption key to host \'%s\'' % self.host)
        enc_key = fr_row['key']
        
        # Return the decryption key
        return valid(json.dumps({ 'key': enc_key }))

class FormulaRegister:
    """
    This class is invoked after a host has decrypted a formula package and is
    about to run the formula. This confirms that the host actually exists and that
    the package is registered to the host. If the package has not yet been verified
    an error is returned.
    """
    def __init__(self, parent):
        """
        Initialize the formula registration utility.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        self.api = parent

    def launch(self):
        """
        Main method for registration of a formula run from a managed host. Validates
        the host and package parameters. Sets the 'decrypted' field for the formula
        registration entry to True if everything looks OK. If an error is returned,
        the host will abort the formula run.
        """
        required = ['pkg_uuid', 'host_uuid']
        for key in required:
            if not key in self.api.data:
                return invalid(self.api.log.error('Missing required key \'%s\' in request body' % key))
        self.pkg  = self.api.data['pkg_uuid']
        self.host = self.api.data['host_uuid']
        
        # Log the registration attempt
        self.api.log.info('Host \'%s\' registering run of pacakge \'%s\'' % (self.host, self.pkg))
        
        # Make sure the host exists
        if not DBHostDetails.objects.filter(uuid=self.host).count():
            return invalid(self.api.log.error('Failed to locate host \'%s\' in the database' % self.host))

        # Make sure the package is registered to the host
        if not DBFormulaRegistry.objects.filter(host=self.host).filter(uuid=self.pkg).count():
            return invalid(self.api.log.error('The requested package \'%s\' does not exist or is not registered to the host \'%s\'' % (self.pkg, self.host)))

        # Get the formula registration row
        fr_row = DBFormulaRegistry.objects.filter(host=self.host).filter(uuid=self.pkg).values()[0]
        
        # Make sure the formula has been verified
        if not fr_row['verified']:
            return invalid('The submitted package run registration has not been verified')
        
        # Make sure the package hasn't already been decrypted
        if fr_row['decrypted']:
            return invalid(self.api.log.error('The requested pacakge \'%s\' has already been decrypted' % self.pkg))
        self.api.log.info('Package \'%s \'has been verified, proceeding with run' % self.pkg)
        
        # Update the formula registry
        self.api.socket.loading('Agent registered package execution...')
        DBFormulaRegistry.objects.filter(host=self.host).filter(uuid=self.pkg).update(decrypted = True)
        
        # Return a valid response
        return valid()
        
class FormulaGet:    
    """
    Retrieve details about either a specific formula or all authorized formulas.
    """
    def __init__(self, parent):
        """
        Initialize the formula retrieval utility.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        self.api     = parent

        # Target formula
        self.formula = self.api.acl.target_object()

    def launch(self):
        """
        Main method for retrieving formula details. If querying all available formulas,
        a list of dictionaries is returned. If querying a single formula, a dictionary
        is returned in the response body.
        """
        
        # Get a list of authorized formula objects
        auth_formulas = self.api.acl.authorized_objects('formula')
            
        # Get specific formula details
        if self.formula:
            
            # If the formula doesn't exist or access denied
            if not self.formula in auth_formulas.ids:
                return invalid(self.api.log.error('Requested formula <%s> not found or access denied' % self.formula))
            
            # Return the formula details
            return valid(auth_formulas.extract(self.formula))
        
        # Get all formulas
        else:
            
            # Return all formulas
            return valid(auth_formulas.details)
        
class FormulaDelete:
    """
    This class will completely remove a formula from the database, and it will
    no longer be available. This deletes the formula details entry as well as any
    formula templates.
    
    This does not effect any hosts which have already applied this formula.
    """
    def __init__(self, parent):
        """
        Initialize the formula delete utility.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        self.api     = parent
    
        # Target formula
        self.formula = self.api.acl.target_object()
    
    def launch(self):
        """
        Primary method for deleting the formula. Makes sure the formula ID actually
        exists. First deletes the formula details, then deletes any formula templates.
        """
        
        # Construct a list of authorized formulas
        auth_formulas = self.api.acl.authorized_objects('formula', 'formula/get')
        
        # Make sure the formula actually exists and is accessible
        if not self.formula in auth_formulas.ids:
            return invalid(self.api.log.error('Cannot delete formula <%s>, not found in database or access denied' % self.formula))
        
        # Delete the formula
        try:
            DBFormulaDetails.objects.filter(uuid=self.formula).delete()
            self.api.log.info('Deleted formula details for <%s>' % self.formula)
        
        # Critical error when deleting formula
        except Exception as e:
            return invalid(self.api.log.exception('Failed to delete formula <%s>: %s' % (self.formula, str(e))))
        
        # Delete all formula templates
        try:
            DBFormulaTemplates.objects.filter(formula=self.formula).delete()
            self.api.log.info('Deleted all templates for formula <%s>' % self.formula)
            
        # Critical error when deleting formula template
        except Exception as e:
            return invalid(self.api.log.exception('Failed to delete formula <%s> templates: %s' % (self.formula, str(e))))
        
        # Return the response
        return valid('Successfully deleted formula', {
            'uuid': self.formula
        })
    
class FormulaRunBase(object):
    """
    Base utility class for both FormulaServiceRun and FormulaUtility run. Performs a number
    of steps to run the supplied formula.
    
    1.) Set and validate the formula ID
    2.) Set and validate the target host
    3.) Construct target host attributes and connect parameters
    4.) Set the formula run mode, either 'managed' or 'unmanaged'
    5.) Validate the JSON structure of the formula request
    6.) Construct parameters to be passed to the FormulaParse utility
    7.) Encrypt and register the package in the database to be sent to the host (managed mode)
    8.) Copy the formula package to the host and run
    9.) If successfull, create a database entry for the target host with formula details
    
    :todo: This class is currently a large monolithic block of code, and needs to broken up
    into parts. Contains a lot of conditionals to differentiate between host types and formula
    run types ('install' vs. 'uninstall' as well as 'service' vs. utility). Need to do some
    major cleanup here, but for now it works.
    """
    def __init__(self, parent):
        """
        Initialize the utility formula class.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        self.api      = parent
        
        # API data container
        self.data     = None
        
        # Attributes
        self.f_type   = None # Formula type
        self.r_type   = None # Formula run type
        self.h_type   = None # Target host type
        self.connect  = None # Host connect attributes
        self.manifest = None # Formula manifest
    
    def _set_attrs(self):
        """
        Set required attributes after loading API data.
        """
        self.formula      = self.data['uuid']
        self.host         = self.data['host']
        self.host_details = None
        self.mode         = self.data['mode']
    
    def _set_host(self):
        """
        Set any required host parameters prior to running the formula.
        """
        
        # Get a list of authorized hosts
        auth_hosts = self.api.acl.authorized_objects('host', 'host/get')
        
        # Valid host types
        h_types = [H_LINUX, H_WINDOWS]
        
        # Make sure the host exists and is accessible
        if (self.mode == F_MANAGED) and (self.formula != A_WINDOWS):
            if not self.host in auth_hosts.ids:
                return invalid('Failed to run formula, host <%s> not found in database or access denied' % self.host)
        
        # Set the host type from the database in managed mode
        if self.mode == F_MANAGED:
        
            # Extract the host details
            self.host_details = auth_hosts.extract(self.host)
            self.h_type       = self.host_details['os_type']
        
        # Require a <host_type> parameter in unmanaged mode
        else:
            
            # Missing parameter
            if not 'host_type' in self.data: 
                return invalid('Must supply a <host_type> parameter when running in unmanaged mode')
            
            # Invalid parameter
            if not (self.data['host_type'] in h_types):
                return invalid('Invalid <host_type> parameter, must be: %s' % json.dumps(h_types))
        
            # Set the host type parameter and extract host details
            self.h_type       = self.data['host_type']
            self.host_details = self.data
        
        # Set host attributes
        return valid()
    
    def _set_formula(self):
        """
        Retrieve formula attributes and the formula JSON manifest. Make sure the formula
        actually exists in the database. If running in 'managed' mode, check if the formula
        has already been applied to host. If running a 'service' utility, return an HTTP
        error if already applied, otherwise continue.
        
        Also check if the formula has been applied but is currently in an error state.
        """
        
        # Construct a list of authorized formulas
        auth_formulas = self.api.acl.authorized_objects('formula', 'formula/get')
        
        # Make sure the formula actually exists and is accessible
        if not self.formula in auth_formulas.ids:
            return invalid(self.api.log.error('Cannot run formula <%s>, not found in database or access denied' % self.formula))
        
        # Get the formula details
        f_details = auth_formulas.extract(self.formula)
        
        # Set the formula manifest and type
        self.manifest = f_details['manifest']
        self.f_type   = f_details['type']
        
        # If running in managed mode
        if self.mode == F_MANAGED:
            
            # Make sure the formula hasn't already been applied to the host
            if DBHostFormulas.objects.filter(host=self.host).filter(formula=self.formula).count():
                h_formula = DBHostFormulas.objects.filter(host=self.host).filter(formula=self.formula).values()[0]
                if h_formula['exit_status'] == 'error':
                    return invalid(self.api.log.error('Formula <%s> is in an error state on host <%s>. Please clear the error state before re-running' % (self.formula, self.host)))
                else:
                    
                    # If the formula is of 'service' type and attempting installation
                    if (self.f_type == F_SERVICE) and (self.r_type == F_INSTALL):
                        return invalid(self.api.log.error('Formula <%s> has already been applied to host <%s> - cannot re-apply a <%s> formula' % (self.formula, self.host, F_SERVICE)))
                    
                    # If the formula is of 'utility' type
                    if (self.f_type == F_UTILITY):
                        pass
                    
        # Set formula attributes
        return valid()
 
    def _set_connect(self):
        """
        Set connection attributes for the host depending on the mode, host type, and
        formula ID. If running the agent installation for Linux, required an SSH password.
        If running the agent installation for Windows, require the installed deployment
        key. Otherwise extract the connection data from the database.
        """
        
        # Linux / Unmanaged
        if (self.mode == F_UNMANAGED) and (self.h_type == H_LINUX):
            
            # Require connection parameters
            if not 'connect' in self.data or not isinstance(self.data, dict):
                return invalid(self.api.log.error('Failed to run unmanaged formula, missing or invalid connection parameters'))
            self.connect = self.data['connect']
        
            # Look for required connection parameters
            for r in ['host', 'port', 'user', 'passwd']:
                if not r in self.connect or not self.connect[r]:
                    return invalid(self.api.log.error('Failed to run unmanaged formula, missing required <%s> connect parameter' % r))
        
        # Windows / Agent Installation
        elif (self.formula == A_WINDOWS):
            
            # Require connection parameters
            if not 'connect' in self.data or not isinstance(self.data, dict):
                return invalid(self.api.log.error('Failed to run unmanaged formula, missing or invalid connection parameters'))
            self.connect = self.data['connect']
        
            # Look for required connection parameters
            for r in ['host', 'port', 'user', 'key']:
                if not r in self.connect or not self.connect[r]:
                    return invalid(self.api.log.error('Failed to run unmanaged formula, missing required <%s> connect parameter' % r))
        
        # Managed
        else:
            
            # Get the host connection parameters
            self.connect  = HostConnect().details(uuid=self.host)
            
        # Connection parameters set
        return valid()
        
    def _validate(self, data):
        """
        Wrapper method for validating various parts of the formula run process. Calls the
        following methods:
        
        1.) _set_mode()
        2.) _set_host()
        3.) _set_id()
        4.) _set_connect()
        
        Construct the base system information dictionary to be supplied to the FormulaParse
        utility, and also validate fieldsets to make sure all required parameters are set.
        """
        self.api.log.info('Validating formula run request data: %s' % str(self.data))
        
        # Set the target host
        host_rsp   = self._set_host()
        if not host_rsp['valid']:
            return host_rsp
        
        # Set the formula attributes
        formula_rsp = self._set_formula()
        if not formula_rsp['valid']:
            return formula_rsp
        
        # Set the connection parameters
        connect_rsp = self._set_connect()
        if not connect_rsp['valid']:
            return connect_rsp
        
        # Get system information
        self.sys_info = {
            'os':           self.host_details['sys']['os']['type'].lower(),
            'uuid':         self.host,
            'distro':       self.host_details['sys']['os']['distro'], 
            'distroLower':  self.host_details['sys']['os']['distro'].lower(),
            'version':      self.host_details['sys']['os']['version'], 
            'versionMajor': re.compile('(^[^\.]*)\.[0-9]*$').sub(r'\g<1>', self.host_details['sys']['os']['version']),
            'versionMinor': re.compile('^[^\.]*\.([0-9]*$)').sub(r'\g<1>', self.host_details['sys']['os']['version']),
            'arch':         self.host_details['sys']['os']['arch'],
            'memory':       self.host_details['sys']['memory']['total'],
            'kernel':       None if not ('kernel' in self.host_details['sys']['os']) else self.host_details['sys']['os']['kernel'],
            'csd':          None if not ('csd' in self.host_details['sys']['os']) else self.host_details['sys']['os']['csd'],
            'release':      self.host_details['sys']['os']['release']
        }
        
        # If any fieldsets are set
        if 'fieldsets' in self.manifest:
            required_params = []
            for fieldset_obj in self.manifest['fieldsets']:
                for field_obj in fieldset_obj['fields']:
                    if field_obj['required'] == 'yes':
                        required_params.append(field_obj['name'])
            
            # Make sure all required parameters are set
            for required in required_params:
                if required not in self.data or not self.data[required]:
                    return invalid(self.api.log.error('Failed to run formula <%s>, missing required <%s> parameter' % (self.formula, required)))         
        
        # Parameters look OK
        return valid()

    def _encrypt_pkg(self, pkg_uuid, pkg_path, register=True):
        """
        If running in managed mode, encrypt and register the package before deploying:
        
        1.) Encrypt the package with a 32 character key
        2.) Store the encryption key and package checksum in the database
        """
        fs = FileSec()
        
        # Generate an encryption key and set the encrypted file path
        try:
            self.enc_key = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(32))
            enc_file     = '%s.enc' % pkg_path
            
            # Encrypt the package
            fs.encrypt(pkg_path, enc_file, self.enc_key)
            
            # Generate a checksum of the encrypted file
            checksum = fs.checksum(enc_file)
        except Exception as e:
            return invalid(self.api.log.error('Failed to generate encrypted formula package: %s' % e))
        
        # Update the formula registry
        if register:
            try:
                pkg_registered = DBFormulaRegistry(
                    formula   = self.formula,
                    uuid      = pkg_uuid,
                    host      = self.host,
                    checksum  = checksum,
                    key       = self.enc_key,
                    verified  = False,
                    decrypted = False          
                )
                pkg_registered.save()
            except Exception as e:
                return invalid(self.api.log.error('Failed to register encrypted formula package: %s' % e))
            self.api.log.info('Registered package: %s' % pkg_uuid)
        self.api.log.info('Encrypted package: %s' % pkg_uuid)

        # Return the encrypted package path
        return valid(enc_file)
        
    def _sanitize_fp(self, params):
        """
        Basic method to sanitize formula parameters before sending to the FormulaParse
        utility. Remove any un-needed or secure parameters.
        """
        sanitized = copy.copy(params)
        
        # Keys to remote
        remove_keys = ['action', 'sys', 'connect', 'mode', 'uuid']
        for key in remove_keys:
            if key in sanitized:
                del sanitized[key]
        return sanitized
      
    def _format_cmd(self, root=None, action=None, **kwargs):
        """
        Formula the remote command used to execute the package on the remote host when
        running in managed mode. Uses the CloudScape agent utility.
        """
        opt_args = []
        for k,v in kwargs.iteritems():
            opt_args.append('--%s %s' % (k,v))
        return '%s %s %s' % (root, ' '.join(opt_args), action)
        
    def _formula_exec_cmd(self, mode, pkg_uuid):
        """
        Wrapper method for the '_format_cmd' method. Generates the command array to be
        passed to the remote connect object to run the package on the remote server depending
        on the target host and mode.
        """
        
        # Windows hosts
        if self.h_type == H_WINDOWS:
            auto_decrypt  = [self._format_cmd('agent', A_EXECPKG, uuid=pkg_uuid, decrypt=self.enc_key)]
            agent_decrypt = [self._format_cmd('agent', A_EXECPKG, uuid=pkg_uuid)]
            
            # Return the appropriate command
            return auto_decrypt if (self.formula == A_WINDOWS) else agent_decrypt
        
        # Linux hosts
        if self.h_type == H_LINUX:
            managed_run   = [self._format_cmd('sudo /usr/bin/cloudscape-agent', A_EXECPKG, uuid=pkg_uuid)]
            unmanaged_run = ['{sudo} tar xzf /tmp/%s.tar.gz -C /tmp' % pkg_uuid, '{sudo} python /tmp/%s/main.py' % pkg_uuid]
            
            # Return the appropriate command
            return managed_run if (mode == F_MANAGED) else unmanaged_run
        
    def _cleanup(self, pkg_uuid):
        """
        Cleanup and local temporary package files and directories after successfull deploying
        the package to the remote host. If the formula run fails with an exception due to a
        bug in the code, the package files will remain on the local host for debugging.
        """
        try:
            self.api.log.info('Cleaning up archive files for package: %s' % pkg_uuid)
            os.unlink('/tmp/%s.tar.gz' % pkg_uuid)
            os.unlink('/tmp/%s.tar.gz.enc' % pkg_uuid)
        except:
            pass
        
    def launch(self, data=None, type=F_INSTALL):
        """
        Main method for the FormulaRunBase utility. Validate all formula parameters, and constructs
        any required objects to be passed to the FormulaParse utility class. Also checks to make sure
        the target host is supported for this formula.
        
        Generates the formula package and encrypts if running in managed mode. Deploys the package
        to the remote server and runs. Does not wait for the script to finish running before closing
        the SSH connection.
        
        The formula script is first run without invoking the main body of code, then uses a subprocess
        to run the main body as well as the monitor thread. Unless an exception is through when invoking
        the subprocess, an exit code of '0' is returned. The CloudScape agent will parse the log files
        and return any errors if problems happen during the run.
        
        :param data: Optional data dictionary to override parameters in 'self.api.data'
        :type data: dict
        :param type: Used mainly for service utilities, can either be 'install' or 'uninstall'
        :type type: str
        """
        self.r_type = type
        
        # Allow overriding of the API data object from an inter-API call
        self.data   = data if (data and isinstance(data, dict)) else copy.copy(self.api.data)
        
        # Set attributes
        self._set_attrs()
        
        # Validate the formula run data
        try:
            formula_rsp = self._validate(data)
            if not formula_rsp['valid']:
                return formula_rsp
        except Exception as e:
            return invalid(self.api.log.exception('Encountered exception when validating formula run: %s' % str(e)))
        
        # Build a list of required formulas
        formula_requires = [] if not ('requires' in self.manifest['formula']) else self.manifest['formula']['requires']
        
        # Make sure the target host is supported
        if not host_utils.supported(self.sys_info['distro'], self.sys_info['version'], self.sys_info['arch'], self.manifest['formula']['supports']):
            return invalid(self.api.log.error('The formula <%s> is not supported on host <%s>' % (self.formula, self.host)))
        self.api.log.info('Formula <%s> support validation success for host <%s>' % (self.formula, self.sys_info['uuid']))
        
        # Sanitize the formula parameters
        run_params = self._sanitize_fp(self.data)
        
        # Generate a formula package
        self.api.socket.loading('Generating agent formula package...')
        try:
            formula_rsp = FormulaParse(formula=self.data['uuid'], params=run_params, sys=self.sys_info, mode=self.mode).generate(self.r_type)
            if not formula_rsp['valid']:
                return invalid(self.api.log.error('Failed to generate the formula package for <%s>' % self.formula))
        except Exception as e:
            return invalid(self.api.log.exception('Exception while parsing formula: %s' % str(e)))
        
        # Store the package UUID and file path
        pkg_uuid = formula_rsp['content']['uuid']
        pkg_file = formula_rsp['content']['pkg']
        self.api.log.info('Generated <%s> formula package: %s' % (self.formula, pkg_file))
        
        # Open a connection to the server
        self.api.socket.loading('Deploying agent formula package...')
        remote_rsp = RemoteConnect(sys_type=self.h_type, conn=self.connect).open()
        if not remote_rsp['valid']:
            return remote_rsp
        remote = remote_rsp['content']
        
        """ 
        Managed Mode: Package Encryption
        
        If running in managed mode, the CloudScape agent will unpack and run the formula. The package
        is first encrypted on the server, then a SHA256 checksum is generated. When the target host
        runs the package UUID, first the checksum/UUID/host combination is validated, then the key to
        decrypt is passed back to the target host.
        """
        if self.mode == F_MANAGED:
            register = False if (self.formula == A_WINDOWS) else True
            enc_rsp = self._encrypt_pkg(pkg_uuid, pkg_file, register)
            if not enc_rsp['valid']:
                return enc_rsp
            enc_file = enc_rsp['content']
        
            # Remote file and run command
            remote_file = np('%s/home/formula/%s.tar.gz.enc' % (C_BASE, pkg_uuid), t=self.h_type)
            remote_cmd  = self._formula_exec_cmd(self.mode, pkg_uuid)
        
            # Copy the formula package to the remote server
            remote.send_file(local=enc_file, remote=remote_file, mode=644)
        
            # Run the formula on the remote server
            self.api.log.info('Preparing to run <%s> formula <%s> on host <%s>' % (self.mode, self.formula, self.connect['host']))
            output = remote.execute(remote_cmd)
            remote.close()
        
        """ 
        Unmanaged Mode: Manual Deployment
        
        If running in unmanaged mode, the formula package will be executed directly as root. This should
        only be used for now when installing the agent and setting up the agent account and root-wrapper
        scripts.
        """
        if self.mode == F_UNMANAGED:
        
            # Remote file and run command
            remote_file = {
                H_LINUX:   '/tmp/%s.tar.gz' % pkg_uuid,
                H_WINDOWS: '%s\\home\\formula\\%s.tar.gz' % (W_BASE, pkg_uuid)
            }
            remote_cmd  = self._formula_exec_cmd(self.mode, pkg_uuid)
        
            # Copy the formula package to the remote server
            remote.send_file(local=remote_file[self.h_type], mode=644)
        
            # Run the formula on the remote server
            self.api.log.info('Preparing to run <%s> formula <%s> on host <%s>' % (self.mode, self.formula, self.connect['host']))
            output = remote.execute(remote_cmd)
            remote.close()
        
        # Check if any errors occured
        for cmd in output:
            if cmd['exit_code'] != 0:
                return invalid('Formula run on remote server failed, command <%s> exited with code <%s>: %s' % (cmd['command'], cmd['exit_code'], str(cmd['stderr'])))
        self.api.socket.loading('Formula package deployment success...')
    
        # Clean up local files
        self._cleanup(pkg_uuid)
    
        # Only update the host formulas in managed mode for existing hosts
        if (self.mode == F_MANAGED) and (self.formula != A_WINDOWS):
    
            # Build the run parameters object
            run_params_obj = []
            for k,v in run_params.iteritems():
                field_type = 'text'
                if 'fieldsets' in self.manifest:
                    for fieldset_obj in self.manifest['fieldsets']:
                        for field_obj in fieldset_obj['fields']:
                            if field_obj['name'] == k:
                                field_type = field_obj['type']
                run_params_obj.append({'name': k, 'type': field_type, 'value': v})
            
            # Disable the current flag on previous formula runs
            DBHostFormulas.objects.filter(host=self.sys_info['uuid']).filter(formula=self.formula).update(current=False)
            
            # Update the formula details for the host
            DBHostFormulas(
                host        = DBHostDetails.objects.get(uuid=self.sys_info['uuid']),
                formula     = self.formula,
                exit_status = F_RUNNING,
                exit_code   = 0,
                exit_msg    = 'Currently running formula',
                requires    = json.dumps(formula_requires),
                run_params  = json.dumps(run_params_obj),
                current     = True
            ).save()
            return valid('Formula <%s> has been launched on host <%s>' % (self.formula, self.host))
        
        # Return the host run parameters
        if (self.mode == F_UNMANAGED) or (self.formula == A_WINDOWS):
            return valid()
    
class FormulaServiceRun(FormulaRunBase):
    """
    Handler class for service formula runs. Inherits from the FormulaRunBase class
    along with the FormulaUtilityRun class. Service formulas can be applied once
    per host, and are typically used to set up applications such as servers. Also
    used to manage removal of the application with the 'uninstall.template' file 
    if provided, as well as updates.
    
    :todo: Current have not implemented any update features.
    :todo: Need to cleanup the formula uninstallation process.
    """
    def __init__(self, parent):
        """
        Initialize the formula service run utility.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        super(FormulaServiceRun, self).__init__(parent)
    
class FormulaUtilityRun(FormulaRunBase):
    """
    Handler class for utility formula runs. Inherits from the FormulaRunBase class
    along with the FormulaServiceRun utility. Utility formulas can be run multiple
    times per host, and are typically used for performing repeat administrative tasks,
    such as network or firewall configuration, backups, etc.
    """
    def __init__(self, parent):
        """
        Initialize the utility formula class.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        super(FormulaUtilityRun, self).__init__(parent)
    
class FormulaGroupRun:
    """
    Handler class for group formula runs. Acts as a wrapper for either service or
    utility formulas for groups of nodes. Depending on the type of group being applied,
    you may supply a 'group_name' parameter to put the nodes in a logical group for
    administrative purposes. This also allows you to retrieve run parameters for a 
    specific group and add more nodes later.
    """
    def __init__(self, parent):
        """
        Initialize the formula group run utility.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        self.api           = parent
        
        # Formula UUID / details / manifest
        self.formula       = self.api.acl.target_object()
        self.details       = None
        self.manifest      = None
        
        # Authorized formulas / hosts
        self.auth_formulas = self.api.acl.authorized_objects('formula', 'formula/get')
        self.auth_hosts    = self.api.acl.authorized_objects('host', 'host/get')
        
        # Group name / set group flag
        self.group_name    = None
        self.set_group     = False
        
        # Worker threads and return object
        self.thread_w      = []
        self.thread_r      = {}
        
        # Host targets
        self.targets       = []
        
    def _extract_val(self, _v,_d,_p):
        """
        Helper method used to recursively extract and replace value placeholder tags
        from target parameters.
        """
        
        # Extract and replace any parameter keys first
        if '@' in _v:
            pk = re.compile(r'^.*@([^,;:%\s\[\]\.\{\}]*).*$').sub(r'\g<1>', _v)
            _v = _v.replace('@%s' % pk, _d[pk])
            return self._extract_val(_v,_d,_p)
        else:
            
            # Extract and replace any API object details next
            if re.match(r'^.*\{[^\}]*\}.*$', _v):
                qsupported = False
    
                # Extract host data
                if re.match(r'^.*\{%HOST:[^%]*%.*$', _v):
                    qsupported = True
                    host_uuid  = re.compile(r'^.*\{%HOST:([^%]*)%.*$').sub(r'\g<1>', _v)
                    host_query = re.compile(r'^.*\{%%HOST:%s%%:([^\}]*)\}.*$' % host_uuid).sub(r'\g<1>', _v)
    
                    # Get the host details
                    host_details = DBHostDetails.objects.filter(uuid=host_uuid).values()[0]
    
                    # Set the replacement regex and value
                    rset = re.compile(r'(^.*)\{%%HOST:%s%%:[^\}]*\}(.*$)' % host_uuid)
                    rval = obj_extract(host_details, filter=host_query, auto_quote=False)
    
                # If the query is supported
                if qsupported:
                    _v = rset.sub(r'\g<1>%s\g<2>' % rval, _v)
    
                # If any more replacements exist
                if re.match(r'^.*\{[^\}]*\}.*$', _v):
                    return self._extract_val(_v,_d,_p)
                else:
                    return _v
            else:
                return _v
        
    def _set_formula(self):
        """
        Set and validate formula attributes for the group formula run. Makes sure a
        formula ID is specified and valid. Loads the formula body from the database
        and makes sure that host targets have been set in the formula manifest.
        
        Once validated, parse the host 'targets' block and extract parameters, such
        as formula ID and any other runtime parameters for each respective formula.
        """
        
        # If the formula does not exist or is not authorized
        if not self.formula in self.auth_formulas.ids:
            return invalid('Failed to run group formula <%s>, not found or access denied' % self.formula)
        
        # Load the formula details
        self.details  = self.auth_formulas.extract(self.formula)
        
        # Get the group formula manifest
        self.manifest = self.details['manifest']
        
        # Make sure host targets are set
        if not 'targets' in self.manifest:
            return invalid('Must define a <targets> block in group formula manifest')
        
        # Generate a global event ID
        event_id = str(uuid4())
        
        # Load the host targets
        for t in self.manifest['targets']:
            
            # Parse the parameters
            params = {}
            for k,v in t['params'].iteritems():
                if '@' in v:
                    params[k] = self._extract_val(v, self.api.data, params)
                else:
                    params[k] = v
            
            # Internal parameters
            pi = { 
                'mode':       F_MANAGED, 
                'host_type':  host_utils.get_host_type(params['host']),
                'uuid':       t['formula'],
                'events':     'True',
                'events_id':  event_id
            }
            
            # Set any default parameters
            for k,v in pi.iteritems():
                if not k in params:
                    params[k] = v
            
            # Make sure the formula exists
            if not t['formula'] in self.auth_formulas.ids:
                return invalid('Target formula <%s> not found or access denied' % t['formula'])
            
            # Set the host target
            self.targets.append({
                'formula': t['formula'],
                'params':  params
            })
            
        # Log the constructed object and return valid
        return valid(self.api.log.info('Constructed group formula targets: %s' % json.dumps(self.targets)))
        
    def _set_group(self):
        """
        If a group name is supplied, make sure the name is not already in use. Also
        set the 'set_group' boolean flag to True.
        """
        if not 'group_name' in self.api.data:
            self.set_group = False
            return valid()
        self.set_group  = True
        self.group_name = self.api.data['group_name']
        
        # Make sure the group name is available
        if DBHostGroups.objects.filter(name=self.group_name).count():
            return invalid('Host group name <%s> is already in use' % self.group_name)
        return valid()
        
    def _check_hosts(self):
        """
        Check if all the hosts support the formula.
        """
        for t in self.targets:
            target_host = t['params']['host']
            
            # Make sure the host exists and is accessible
            if not target_host in self.auth_hosts.ids:
                return invalid('Target host <%s> not found or access denied' % target_host)
            self.api.log.info('Parsing target host <%s>: params=%s' % (target_host, json.dumps(t['params'])))
            
            # Get host OS information
            os_info = self.auth_hosts.extract(target_host)['sys']['os']
            
            # Make sure the host is supported
            if not host_utils.supported(os_info['distro'], os_info['version'], os_info['arch'], self.manifest['formula']['supports']):
                return invalid(self.api.log.error('The formula <%s> is not supported on host <%s>' % (self.formula, target_host)))
            self.api.log.info('Formula <%s> support validation success for host <%s>' % (self.formula, target_host))
        
        # All hosts supported
        return valid()
        
    def _formula_worker(self, formula, params):
        """
        Thread worker for running the target formula ID on the host.
        
        :param formula: The formula ID to run
        :type formula: str
        :param params: The formula runtime parameters
        :type params: dict
        """
        
        # Extract the host UUID
        host_uuid = params['host']
        
        # Set the formula ID and mode in the parameters
        params.update({
            'uuid': formula,
            'mode': F_MANAGED
        })
        
        # Get the formula details
        f_details = self.auth_formulas.extract(formula)
        
        # Log the formula run
        self.api.log.info('Preparing to run formula <%s> on host <%s> with params: %s' % (formula, host_uuid, params))
        
        # Try to run the formula
        try:
            
            # Service formula
            if f_details['type'] == 'service':
                self.thread_r[host_uuid] = FormulaServiceRun(self.api).launch(params, type=F_INSTALL)
                
            # Utility formula
            if f_details['type'] == 'utility':
                self.thread_r[host_uuid] = FormulaUtilityRun(self.api).launch(params)
            
        # Critical when running host formula
        except Exception as e:
            self.thread_r[host_uuid] = invalid(self.api.log.exception('Failed to run formula <%s> on host <%s>: %s' % (formula, host_uuid, str(e))))
        
    def launch(self):
        """
        Primary method for running the formula group utility. Initialized with the APIBase
        object, which contains various utilities and attributes common to all API endpoints.
        Also provides access to the formatted API request object.
        
        This method validates the formula ID parameter and sets formula attributes and targets
        for each node being configured. If a group name is supplied, validate the group name
        and set up any required database entries.
        
        Runs the respective formula for each node that has been specified in the formula
        manifest 'targets' block with any additional runtime parameters.
        """
        
        # Set the formula attributes
        try:
            f_status = self._set_formula()
            if not f_status['valid']:
                return f_status
        except Exception as e:
            return invalid(self.api.log.exception('Failed to set formula attributes: %s' % str(e)))
        
        # Set the group attributes
        try:
            g_status = self._set_group()
            if not g_status['valid']:
                return g_status
        except Exception as e:
            return invalid(self.api.log.exception('Failed to set group attributes: %s' % str(e)))
        
        # Check host support
        try:
            h_status = self._check_hosts()
            if not h_status['valid']:
                return h_status
        except Exception as e:
            return invalid(self.api.log.exception('Failed to validate host support: %s' % str(e)))
        
        # Run the target formula on each host
        for t in self.targets:
            self.api.log.info('Running formula worker for <%s> on host <%s>' % (t['formula'], t['params']['host']))
        
            # Start the worker thread
            t = Thread(target=self._formula_worker, args=[t['formula'], t['params']])
            self.thread_w.append(t)
            t.start()
        
        # Join the worker threads until they finish
        for t in self.thread_w:
            t.join()
        
        # Get the results once the threads are complete
        failed_hosts = {}
        for h,r in self.thread_r.iteritems():
            if not r['valid']:
                failed_hosts[h] = r['content']
            else:
                self.api.log.info('Formula run on host <%s> success' % h)
        if failed_hosts:
            host_list = []
            for k,v in failed_hosts.iteritems():
                host_list.append('Formula run error <%s>: %s' % (k, str(v)))
            return invalid(self.api.log.error(', '.join(host_list)))
        
        # If a group name was specified
        if self.set_group:
            self.api.log.info('Creating formula host group <%s>' % self.group_name)
        
            # Set the group metadata and members
            group_meta    = {
                'targets': {},
                'params':  {}
            }
            group_members = []
            for t in self.targets:
                group_meta['targets'][t['params']['host']] = {
                    'formula': t['formula'],
                    'params':  t['params']
                }
                group_members.append(t['params']['host'])
            for k,v in self.api.data.iteritems():
                group_meta['params'][k] = v
        
            # Create the group entry and group member entries
            try:
                
                # Host group
                host_group = DBHostGroups(
                    uuid     = uuid4(),
                    name     = self.group_name,
                    formula  = self.formula,
                    metadata = json.dumps(group_meta)
                )
                host_group.save()
                self.api.log.info('Created database entry for host group <%s>' % self.group_name)
                
                # Add each host to the host_group_members table
                for host in group_members:
                    group_member = DBHostGroupMembers(
                        host  = DBHostDetails.objects.filter(uuid=host).get(),
                        group = host_group
                    )
                    group_member.save()
                    self.api.log.info('Added host <%s> to group <%s>' % (host, self.group_name))
                    
            # Critical error when creating host group entry
            except Exception as e:
                return invalid(self.api.log.exception('Failed to create host group entry: %s' % str(e)))
        
        # Formula group run success
        return valid('Successfully ran group formula <%s>' % self.formula)
    
class FormulaCreate:
    """
    Create either a new service, utility, or group formula. This will create a basic manifest
    and template files if required.
    """
    def __init__(self, parent):
        """
        Initialize the formula creation utility.
        
        :param parent: The APIBase parent object
        :param type: L{APIBase}
        """
        self.api     = parent
        
        # New formula parameters
        self.formula = None
        
    def _validate(self):
        """
        Validate the formula creation properties, make sure the formula ID isn't already in use,
        make sure all required attributes are set, etc.
        """
        
        # Set the new formula parameters
        self.formula = {
            'uuid':     str(uuid4()),
            'name':     self.api.data['name'],
            'label':    self.api.data['label'],
            'desc':     self.api.data['desc'],
            'type':     self.api.data['type'],
            'internal': self.api.data['internal'] 
        }
        self.api.log.info('Creating new formula: uuid=%s, name=%s, label=%s' % (self.formula['uuid'], self.formula['name'], self.formula['label']))
        
        # Check if the formula already exists
        if DBFormulaDetails.objects.filter(name=self.formula['name']).count() != 0:
            return invalid(self.api.log.error('Formula name <%s> already exists in the database' % self.formula['name']))
        
        # Formula parameters look valid
        return valid()
        
    def launch(self):
        """
        Primary method for running the formula creation utility. Automatically generates
        a skeleton formula manifest as well as any default template files defined in this
        method.
        
        The formula manifest is stored in a text field in the database in JSON format, and
        the tempates are store in a text field as Base64 encoded data. Template files that
        inherit from the worker template are set up with any required includes and block
        definitions.
        """
        
        # Default template string value
        def_tstr   = '{# Load the base template and open the main block #}\n' \
                     '{% extends "formula/base.template" %}\n' \
                     '{% load extras %}\n' \
                     '{% block main %}\n\n' \
                     '{# Template contents here #}\n\n' \
                     '{# Close out the main block #}\n' \
                     '{% endblock %}' 
        
        # Validate the request
        req_status = self._validate()
        if not req_status['valid']:
            return req_status
        
        # Base templates
        base_templates = {
            F_UTILITY: ['main.template'],
            F_SERVICE: ['main.template', 'uninstall.template'],
            F_GROUP:   []
        }
        
        # Define the default formula manifest
        manifest = json.dumps({
            'formula': {
                'supports':  OS_SUPPORTED
            }
        })
        
        # Create the new formula row
        try:
            f_new = DBFormulaDetails(
                uuid     = self.formula['uuid'],
                name     = self.formula['name'],
                label    = self.formula['label'],
                desc     = self.formula['desc'],
                manifest = manifest,
                type     = self.formula['type'],
                internal = self.formula['internal'],
                locked   = False
            )
            f_new.save()
            self.api.log.info('Saved new formula <%s:%s> details to database' % (self.formula['uuid'], self.formula['name']))
        except Exception as e:
            return invalid(self.api.log.exception('Failed to create new formula database entry: %s' % str(e)))
        
        # Create the base templates
        for t in base_templates[self.formula['type']]:
            try:
                te    = base64.b64encode(def_tstr)
                t_new = DBFormulaTemplates(
                    formula       = f_new,
                    template_name = t,
                    template_file = te,
                    size          = sys.getsizeof(te)
                )
                t_new.save()
                self.api.log.info('Saved default template file <%s> for formula <%s:%s>' % (t, self.formula['uuid'], self.formula['name']))
            except Exception as e:
                return invalid(self.api.log.exception('Failed to create default formula template <%s>: %s' % (t, str(e))))
        
        # Construct the web socket response
        web_data = {
            'uuid':       self.formula['uuid'],
            'name':       self.formula['name'],
            'label':      self.formula['label'],
            'created':    re.compile(r'(^.*)\..*$').sub(r'\g<1>', str(datetime.datetime.now())),
            'internal':   self.formula['internal'],
            'type':       self.formula['type']
        }
        
        # Create the new formula
        return valid('Successfully created new formula', web_data)
        