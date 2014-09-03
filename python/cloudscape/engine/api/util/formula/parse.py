import os
import re
import copy
import json
import uuid
import errno
import base64
import shutil
import string
import random
import datetime
import collections

# Django Libraries
from django.conf import settings
from django.template import Context, Template
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder

# CloudScape Variables
from cloudscape.common.vars import W_BASE, W_HOME, L_BASE, L_HOME, F_INSTALL, F_UNINSTALL, \
                                   F_UPDATE, A_LINUX, A_WINDOWS, F_MANAGED, F_UNMANAGED, np

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.common import config
from cloudscape.common.utils import valid, invalid
from cloudscape.common.formatter import Formatter
from cloudscape.common.collection import Collection
from cloudscape.engine.api.core import host as host_utils
from cloudscape.engine.api.app.host.models import DBHostDetails, DBHostGroups
from cloudscape.engine.api.app.formula.models import DBFormulaDetails, DBFormulaTemplates

# Configuration and logger objects
CONFIG = config.parse()
LOG    = logger.create(__name__, CONFIG.utils.log)

# Indent String
def _i(s, t=0):
    tab = (' ' * 4) * t
    return '%s%s' % (tab, s)

"""
Formula Variable Mapper

Merge globally defined variables with system and package parameters, and the runtime parameters
supplied to the formula parser. Used when rendering templates, as well as when parsing out strings
from formula manifest groups.
"""
class FormulaMap:
    def __init__(self, params, sys, pkg):
        self.conf       = config.parse()
        self.params     = params
        self.sys        = sys
        self.pkg        = pkg
    
        # Create a collection class
        self.collection = Collection()
    
    """ Mapper Method
    
    Map out global variables and supplied parameters. Return a merged dictionary.
    """
    def mapper(self):
        
        # Define the base map
        base_map   = { 'cs': {
            'base':      np(L_BASE, t=self.sys['os']) if self.sys['os'] == 'linux' else np(W_BASE, t=self.sys['os']),
            'home':      np(L_HOME, t=self.sys['os']) if self.sys['os'] == 'linux' else np(W_HOME, t=self.sys['os']),
            'api_host':  self.conf.server.host,
            'api_port':  self.conf.server.port,
            'api_proto': self.conf.server.proto        
        }}
        LOG.info('Constructed base map: %s' % str(base_map['cs']))
        
        # Construct the package properties map
        pkg_map    = { 'pkg': {}}
        for key, value in self.pkg.iteritems():
            pkg_map['pkg'][key] = value
        LOG.info('Constructed package map: %s' % str(pkg_map['pkg']))
        
        # Construct the parameters map
        params_map = { 'param': {}}
        params_map['param']['events'] = 'False' if not ('events' in self.params) else self.params['events']
        params_map['param']['events_id'] = 'None' if not ('events_id' in self.params) else self.params['events_id']
        for key, value in self.params.iteritems():
            params_map['param'][key] = value
        LOG.info('Constructed params map: %s' % str(params_map['param']))
        
        # Construct the system map
        sys_map    = { 'sys': {}}
        for key, value in self.sys.iteritems():
            sys_map['sys'][key] = value
        LOG.info('Constructed system map: %s' % str(sys_map['sys']))
        
        # Host details map
        host_map   = { 'host': {}}
        for key, value in self.params.iteritems():
            if host_utils.is_host_uuid(value):
                host_details = DBHostDetails.objects.filter(uuid=value).values()[0]
                host_map['host'][key] = host_details
        LOG.info('Constructed host map: %s' % str(host_map['host']))
        
        # If attaching to an existing group
        group_map = { 'group': {}}
        if 'group_uuid' in self.params:
            group_query = DBHostGroups.objects.filter(uuid=self.params['group_uuid']).values()
            if group_query:
                group_map['group'] = json.loads(group_query[0]['metadata'])
        
        # Define the map container
        map_container = [base_map, params_map, sys_map, pkg_map, host_map, group_map]

        # Merge the maps
        map_merged    = {}
        for map in map_container:
            self.collection.merge_dict(map_merged, map)

        # Look for an execution time limit
        map_merged['pkg']['extime'] = 0 if not ('extime' in map_merged['param']) else map_merged['param']['extime']

        # Return the merged map
        return map_merged

"""
Formula Parser
"""
class FormulaParse:
    def __init__(self, formula=None, params={}, sys={}, mode=F_MANAGED):
        
        # Formula run parameters
        self.formula    = formula                   # Formula UUID
        self.params     = copy.deepcopy(params)     # Formula parameters
        self.sys        = sys                       # System parameters
        self.uuid       = uuid.uuid4()              # Package UUID
        self.manifest   = None                      # Formula manifest
        LOG.info('Parsing new formula package <%s>' % self.uuid)
        
        # Get the formula details
        self.details    = DBFormulaDetails.objects.filter(uuid=formula).values()[0]
        
        # Define the package base and archive
        if self.sys['os'] == 'linux':
            self.pkg_base = ('/tmp/%s' % self.uuid) if ((self.formula == A_LINUX) and (mode == F_UNMANAGED)) else ('%s/formula/%s' % (L_HOME, self.uuid))
            self.pkg_arc  = ('/tmp/%s.tar.gz' % self.uuid) if ((self.formula == A_LINUX) and (mode == F_UNMANAGED)) else ('%s/formula/%s.tar.gz' % (L_HOME, self.uuid))
        if self.sys['os'] == 'windows':
            self.pkg_base = '%s\\formula\\%s' % (W_HOME, self.uuid)
            self.pkg_arc  = '%s\\formula\\%s.tar.gz' % (W_HOME, self.uuid)
        
        # Define the local workspace properties
        self.lws = {
            'workspace':  '/tmp/%s' % self.uuid,
            'archive':    '/tmp/%s.tar.gz' % self.uuid,
            'script':     '/tmp/%s/main.py' % self.uuid
        }
        
        # Define the package object
        self.pkg = {
            'formula':    formula,
            'a_linux':    A_LINUX,
            'a_windows':  A_WINDOWS,
            'uuid':       self.uuid,
            'workspace':  np(self.pkg_base),
            'archive':    np(self.pkg_arc),
            'script':     np('%s/main.py' % self.pkg_base, t=self.sys['os']),
            'mode':       F_MANAGED
        }
        
        # Log the formula parameters
        LOG.info('Formula runtime parameters: %s' % self.params)
        LOG.info('Formula system parameters: %s' % self.sys)
        LOG.info('Generating formula package properties: %s' % self.pkg)
        
        # Load the formula variables map
        self.map = FormulaMap(self.params, self.sys, self.pkg).mapper()
        LOG.info('Constructing formula variables map: %s' % str(self.map))
        
        # New collection object
        self.collection = Collection()
    
        # Validate the parameters
        self.status     = self._validate()
    
    """ Formula Validation
    
    Pre-processor to validate arguments passed to the formula parser before actually launching
    the main method.
    """
    def _validate(self):
        
        # Validate the formula
        if not self.formula or not DBFormulaDetails.objects.filter(uuid=self.formula).count():
            return invalid(LOG.error('Missing formula ID parameter or non-existent formula'))
    
        # Required system parameters
        sys_required = ['uuid', 'distro', 'distroLower', 'version', 'versionMajor', 'versionMinor', 'arch', 'memory', 'kernel']
    
        # Validate the system parameters
        LOG.info('Validating required system information fields: %s' % str(sys_required))
        if not self.sys or not isinstance(self.sys, dict):
            return invalid(LOG.error('Missing or invalid system parameters'))
        for key in sys_required:
            LOG.info('Looking for key <%s> in required system parameters' % key)
            if not key in self.sys:
                return invalid(LOG.error('Missing required system parameter <%s>' % key))
                
        # Get the formula manifest
        self.manifest = self.details['manifest']
    
        # Set the maximum execution time
        self.map['pkg']['extime'] = 0 if not ('extime' in self.manifest['formula']) else self.manifest['formula']['extime']
    
        # Validate the fieldsets if defined
        if 'fieldsets' in self.manifest:
            required_fields = []
            for fieldset_obj in self.manifest['fieldsets']:
                for field_obj in fieldset_obj['fields']:
                    if field_obj['required'] == 'yes':
                        required_fields.append(field_obj['name'])
            LOG.info('Parsed required fields for formula <%s>: %s' % (self.formula, str(required_fields)))
                           
            # Make sure all required fields are set
            for field in required_fields:
                LOG.info('Looking for key <%s> in required fields' % field)
                if field not in self.params:
                    return invalid(LOG.error('Failed to parse formula, missing required field <%s> in <formula_manifest> parameters' % param))
    
        # Parameters look OK
        LOG.info('Formula parameter validation success')
        return valid()
    
    """ Target Support Check
    
    Wrapper method to automatically use the supplied system distro, version, and arch. Makes
    a call to the 'cloudscape.engine.api.core.host' module for the 'supported' method.
    Parse each target supported string and compare to the target system for the formula.
    Support strings are in the format <DISTRO_LOWER>/<VERSION>/<ARCH>.
    """
    def _target_supports(self, supported_values):
        return host_utils.supported(self.sys['distro'], self.sys['version'], self.sys['arch'], supported_values)
    
    """ Destination Workspace Path """
    def _dw(self, lp):
        rp = re.compile(r'^.*\/%s\/(.*$)' % self.uuid).sub(r'\g<1>', lp)
        return '%s/%s' % (self.pkg_base, rp)
    
    """ Format Template Method
    
    Helper method to format a stringified method to be printed into the generated Python
    script. Takes the method name as the primary argument, required arguments as the second
    parameter, and a dictionary of optional arguments last.
    """
    def _ftm(self, method, req=[], opt={}):
        
        # Generate the required arguments string
        req_args = []
        for a in req:
            req_args.append(a)
        
        # Generate the keyword arguments string
        opt_args = []
        for k,v in opt.iteritems():
            opt_args.append('%s=%s' % (k,v))
        
        # Create the full arguments string
        all_args = ''
        if req_args:
            all_args += ','.join(req_args)
        if opt_args:
            all_args += ',' + ','.join(opt_args)
        
        # Return the template method string
        return _i('worker.%s(%s)' % (method, all_args))
    
    """ Quote Argument
    
    Basic helper method to auto-quote an argument being passed to the method formatter.
    """
    def _quote(self, arg):
        return np('"%s"' % arg, t=self.sys['os'])
    
    """ Parse Formula String
    
    Helper method to process values in the formula manifest to look for and replace
    variables generated by the formula mapper in this file. Variables should be defined
    by group name as the first index, and the variable name as the second index in the
    mapper.
    """
    def _parse_str(self, str):
        if re.match('^.*{{[^}]*}}.*$', str):
            v = re.compile('^.*{{[ ]?([^ }]*)[ ]?}}.*$').sub(r'\g<1>', str)
            g = re.compile('(^[^\.]*)\.[^\.]*$').sub(r'\g<1>', v)
            n = re.compile('^[^\.]*\.([^\.]*$)').sub(r'\g<1>', v)
            
            # If the variable is mapped, replace the string and return
            if g in self.map and n in self.map[g]:
                ns = re.compile('(^.*){{[ ]?[^}]*[ ]?}}(.*$)').sub('\g<1>%s\g<2>' % self.map[g][n], str)
                LOG.info('Variable match {{ %s }}: <%s> -> <%s>' % (v, str, ns))
                
                # Check if another variable exists
                if re.match('^.*{{[^}]*}}.*$', ns):
                    return self._parse_str(ns)
                return ns
            
            # Throw an error if the variable is not defined
            LOG.error('Tried to use undefined variable {{ %s }} in string subsitution' % v)
            return v
        else:
            return str
    
    """ Load Formula Temmplates
    
    Helper method to load decode and load formula templates into memory.
    """
    def _load_templates(self, template_list):
        template_container = {}
        for template in template_list:
            LOG.info('Loading <%s> formula template <%s>' % (self.formula, template))
            
            # If the template is not found
            if not DBFormulaTemplates.objects.filter(formula=self.formula, template_name=template).count():
                return invalid('Could not locate contents for template <%s>' % template)
                
            # Try to decode the template
            try:
                template_encoded = DBFormulaTemplates.objects.filter(formula=self.formula, template_name=template).values()[0]['template_file']
                template_decoded = base64.decodestring(template_encoded)
            except Exception as e:
                return invalid(LOG.error('An exception ocurred when decoded template <%s> contents' % template))
        
            # Append the template contents to the template container
            template_container[template] = template_decoded
        LOG.info('Loaded all formula templates for <%s>' % self.formula)
        return valid(template_container)
    
    """ Render Template to Path
    
    Helper method to render a template string to a specified path. You can override the template data
    with the third parameter.
    """
    def _template_to(self,s,p,d=None):
        d = self.map if not d else d
        t = Template(s)
        c = Context(d)
        
        # Write the template contents to the destination path
        f = open(p, 'w').write(t.render(c))
    
    """ Read File to Array """
    def r2a(self, path):
        if os.path.isfile(path):
            fh = open(path, 'r')
            fa = fh.readlines()
            fh.close()
            return fa
    
    """ Construct Parent Path """ 
    def construct_path(self, path):
        parent = re.compile(r'(^.*)[\/|\\][^\/|\\]*$').sub(r'\g<1>', path)
        self.mkdir(parent)
    
    """ Make Directory """
    def mkdir(self, dir):
        try:
            os.makedirs(dir)
        except:
            pass
    
    """ Copy File/Directory """
    def cp(self, src, dest):
        try:
            shutil.copytree(src, dest)
        except OSError as e:
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dest)
            else: 
                return False
    
    """ Remove File/Directory """
    def rm(self, path):
        try:
            os.remove(path)
        except:
            try:
                shutil.rmtree(path)
            except:
                return False
    
    def _get_script_template(self, type):
        """
        Return the script template to use when generating the package.
        """
        script_map = {
            F_INSTALL:   'main.template',
            F_UNINSTALL: 'uninstall.template',
            F_UPDATE:    'update.template'
        }
        return script_map[type]
    
    def generate(self, type):
        """
        Worker method for generating the formula package and returning package attributes.
        """
        if not self.status['valid']:
            return self.status

        # Set the active script template
        script_template = self._get_script_template(type)
        LOG.info('Generating formula run type <%s>, using <%s> as main script file template' % (type, script_template))

        # Load the templates
        t_loader = self._load_templates(self.details['templates'])
        if not t_loader['valid']:
            return t_loader
        templates = t_loader['content']

        # Create the package workspace
        self.mkdir(self.lws['workspace'])

        """ Main Template Data
        
        Dictionary of values used when parsing the main script template. These are not
        available inside any optional templates. Optional templates use the pre-constructed
        data map.
        """
        template_data  = {
            'commands':   {},
            'users':      {},
            'files':      {},
            'folders':    {},
            'iptables':   {},
            'services':   {},
            'packages':   {},
            'repository': {}
        }

        # Need to add an extra indent to work with the 'main' method definition
        templates[script_template] = '\n'.join(['    %s' % l for l in templates[script_template].split('\n')])

        # Get the indent count for a specific template entry ID
        def get_indent(id):
            for l in templates[script_template].split('\n'):
                if re.match(r'^.*%s.*$' % id, l):
                    lead = re.compile(r'(^[ ]*)[^ ]*.*$').sub(r'\g<1>', l)
                    lead.expandtabs(4)
                    spaces = len(lead)
                    return (spaces / 4)
            return 0

        """ Parse Formula Manifest 
        
        Parse the formula manifest file and construct any file templates, excluding the main
        installation script template. This part defines command strings, copies resources to
        the package workspace, etc.
        """
        for pkey, pobj in self.manifest.iteritems():
            
            # Service Actions
            if pkey == 'services':
                for svc_obj in pobj:
                    svc_id = svc_obj['id']
                    supported = False
                    for svc_tgt in svc_obj['target']:
                        if self._target_supports(svc_tgt['supports']):
                            supported = True
                            LOG.info('Generating service control entry: <%s>' % svc_id)
            
                            # Required arguments
                            req = [self._quote(svc_tgt['name']), self._quote(svc_tgt['state'])]
        
                            # Optional arguments
                            opt = {
                                'auto': 'None' if not 'auto' in svc_tgt else svc_tgt['auto'],
                            }
        
                            # Generate the template method string
                            svc_cmd = self._ftm('set_service', req, opt)
                            template_data['services'][svc_id] = svc_cmd
                    if not supported:
                        template_data['services'][svc_id] = _i('# Service group <%s> not supported on this system' % svc_id)
            
            # File Actions
            if pkey == 'files':
                self.mkdir('%s/files' % self.lws['workspace'])
                for file_obj in pobj:
                    file_id = file_obj['id']
                    supported = False
                    for file_tgt in file_obj['target']:
                        if self._target_supports(file_tgt['supports']):
                            supported = True
                            
                            # Define the source file in the package
                            file_src = '%s/files/%s' % (self.lws['workspace'], file_id)
                            
                            # Source: Template
                            if file_tgt['source']['type'] == 'template':
                                src_t = file_tgt['source']['name']
                                
                                # Generate and deploy the template file to the package files workspace
                                self._template_to(templates[src_t], file_src, self.map)
                                LOG.info('Generating source file from template: <%s> to <%s>' % (src_t, file_src))
                            
                            # Source: Local
                            if file_tgt['source']['type'] == 'local':
                                src_l = self._parse_str(file_tgt['source']['path'])
                                
                                # Copy the local file to the package files workspace
                                self.cp(src_l, file_src)
                                LOG.info('Copying local package source file: <%s> to <%s>' % (src_l, file_src))
            
                            # Source: Remote
                            if file_tgt['source']['type'] == 'remote':
                                src_r = self._parse_str(file_tgt['source']['path'])
                                
                                # Download the remote file to the package files workspace
                                os.system('curl -o %s %s' % (file_src, src_r))
                                LOG.info('Downloading package source file: <%s> to <%s>' % (src_r, file_src))
            
                            # Make sure the file was created
                            if not os.path.isfile(file_src):
                                LOG.info('Failed to create package source file: <%s>' % file_src)
                                template_data['files'][file_id] = _i('# %s: Failed to create package source file' % file_id)
                            else:
                                LOG.info('Created package source file: <%s>' % file_src)
            
                                # Required arguments
                                req = [self._quote(self._dw(file_src)), self._quote(self._parse_str(file_tgt['dest']['path']))]
            
                                # Optional arguments
                                opt = {
                                    'mode':    'False' if not 'mode' in file_tgt['dest'] else self._quote(file_tgt['dest']['mode']),
                                    'link':    'False' if not 'link' in file_tgt['dest'] else self._quote(file_tgt['dest']['link']),
                                    'context': 'False' if not 'context' in file_tgt['dest'] else self._quote(file_tgt['dest']['context']),
                                    'user':    'False' if not 'user' in file_tgt['dest'] else self._quote(file_tgt['dest']['user']),
                                    'group':   'False' if not 'group' in file_tgt['dest'] else self._quote(file_tgt['dest']['group']),
                                    'force':   'False' if not 'force' in file_tgt['dest'] else file_tgt['dest']['force']
                                }
            
                                # Generate the template method string
                                file_cmd = self._ftm('deploy_file', req, opt)
                                template_data['files'][file_id] = file_cmd
                    if not supported:
                        template_data['files'][file_id] = _i('# File group <%s> not supported on this system' % file_id)
            
            # Repository Actions
            if pkey == 'repository':
                for repo_obj in pobj:
                    repo_id  = repo_obj['id']
                    
                    # Scan each repository target
                    supported = False
                    for repo_tgt in repo_obj['target']:
                        if self._target_supports(repo_tgt['supports']):
                            supported = True
                            
                            # If adding any repository keys
                            repo_keys = 'None'
                            if 'keys' in repo_tgt:
                                repo_keys = json.dumps(repo_tgt['keys'])
                            
                            # Set the repository command
                            template_data[pkey][repo_id] = _i(self._parse_str('worker.add_repo(paths=%s, keys=%s)' % (json.dumps(repo_tgt['source']), repo_keys)))
                        if not supported:
                            template_data[pkey][repo_id] = _i('# Repository group <%s> not supported on this system' % repo_id)
            
            # Package Actions
            if pkey == 'packages':
                for pkg_obj in pobj:
                    pkg_id  = pkg_obj['id']
                    
                    # Scan each packages target
                    supported = False
                    for pkg_tgt in pkg_obj['target']:
                        if self._target_supports(pkg_tgt['supports']):
                            supported = True
                            
                            # Process each action list item
                            for pkg_action, packages in pkg_tgt.iteritems():
                                
                                # Install/Remove/Upgrade Packages
                                if pkg_action in ['install', 'remove', 'upgrade']:
                                    pkg_cmd = _i('worker.set_packages(pkgs=%s, action="%s")' % (
                                        json.dumps(pkg_tgt[pkg_action]), 
                                        pkg_action
                                    ))
                                    template_data[pkey][pkg_id] = pkg_cmd
                        if not supported:
                            template_data[pkey][pkg_id] = _i('# Package group <%s> not supported on this system' % pkg_id)
            
            # IPTables Actions
            if pkey == 'iptables':
                for ipt_obj in pobj:
                    ipt_id  = ipt_obj['id']
                    
                    # Scan each IPTables target
                    supported = False
                    for ipt_tgt in ipt_obj['target']:
                        if self._target_supports(ipt_tgt['supports']):
                            supported = True
                            
                            # Generate the IPTables command
                            ipt_rule_cmd = _i('worker.set_iptables(name="%s", action="%s", chains=%s, save="%s", rules=%s)' % (
                                ipt_tgt['name'], 
                                ipt_tgt['action'],
                                json.dumps(ipt_tgt['chains']), 
                                ipt_tgt['save'],
                                json.dumps(ipt_tgt['rules'])
                            ))
                            template_data[pkey][ipt_id] = ipt_rule_cmd
                        if not supported:
                            template_data[pkey][ipt_id] = _i('# IPTables group <%s> not supported on this system' % ipt_id)
            
            # Folder Actions
            if pkey == 'folders':
                self.mkdir('%s/folders' % self.lws['workspace'])
                for folder_obj in pobj:
                    folder_id = folder_obj['id']
                    supported = False
                    for folder_tgt in folder_obj['target']:
                        if self._target_supports(folder_tgt['supports']):
                            supported = True
                            
                            # Define the source folders path in the workspace
                            folder_src = '%s/folders/%s' % (self.lws['workspace'], folder_id)
                            
                            # Source: Local
                            if folder_tgt['source']['type'] == 'local':
                                src_l = self._parse_str(folder_tgt['source']['path'])
                                
                                # Copy all contents
                                if not ('include' in folder_tgt['source']):
                                    if not os.path.isdir(src_l):
                                        LOG.error('Cannot copy source directory <%s>, does not exist' % src_l)
                                        continue
                                    self.cp(src_l, folder_src)
                                    LOG.info('Copying local package source folder: <%s> to <%s>' % (src_l, folder_src))
            
                                # If explicitly including files
                                if 'include' in folder_tgt['source']:
                                    for _if in folder_tgt['source']['include']:
                                        ifp = '%s/%s' % (src_l, _if)
                                        if not os.path.isfile(ifp) and not os.path.isdir(ifp):
                                            LOG.error('Target include <%s> is not a file or directory in <%s>' % (_if, src_l))
                                            continue
                                        
                                        # Copying files
                                        if os.path.isfile(ifp):
                                            self.mkdir(folder_src)
                                            self.cp(ifp, folder_src)
                                        
                                        # Copying folders
                                        if os.path.isdir(ifp):
                                            self.cp(ifp, '%s/%s' % (folder_src, _if))
                                        LOG.info('Including <%s> in package source <%s>' % (ifp, folder_src))
            
                                # If explicitly excluding files
                                if 'exclude' in folder_tgt['source']:
                                    for _ef in folder_tgt['source']['exclude']:
                                        efp = '%s/%s' % (folder_src, _ef)
                                        if not os.path.isfile(efp) and not os.path.isdir(efp):
                                            LOG.error('Target exclude <%s> is not a file or directory in <%s>' % (_ef, folder_src))
                                            continue
                                        self.rm(efp)
                                        LOG.info('Excluding <%s> from package source <%s>' % (efp, folder_src))
            
                            # Source: Remote
                            if folder_tgt['source']['type'] == 'remote':
                                src_r = self._parse_str(folder_tgt['source']['path'])
                                
                                # TODO: Need a way to recursively download a directory to a path
            
                            # Make sure the directory was created
                            if not os.path.isdir(folder_src):
                                LOG.error('Failed to create package source folder: <%s>' % folder_src)
                                template_data['folders'][folder_id] = _i('# %s: Failed to create package directory' % folder_id)
                            else:
                                LOG.info('Created package source folder: <%s>' % folder_src)
                            
                                # Define the folder modes
                                if 'mode' in folder_tgt['dest']:
                                    mode_flags = ['D', 'F']
                                    mode_list  = []
                                    for flag in mode_flags:
                                        if re.match('^.*[F|D]:[^\/]*.*$', folder_tgt['dest']['mode']):
                                            mode_int = re.compile('^.*%s:([^\/]*).*$' % flag).sub(r'\g<1>', folder_tgt['dest']['mode'])
                                            mode_list.append('%s:' % mode_int)
                                        else:
                                            mode_list.append('%s:False' % flag)
                                    folder_mode = '/'.join(mode_list)
                                else:
                                    folder_mode = 'D:False/F:False'
                                    
                                # Required arguments
                                req = [self._quote(self._dw(folder_src)), self._quote(self._parse_str(folder_tgt['dest']['path']))]
            
                                # Optional arguments
                                opt = {
                                    'mode':    self._quote(folder_mode),
                                    'link':    'False' if not 'link' in folder_tgt['dest'] else self._quote(folder_tgt['dest']['link']),
                                    'context': 'False' if not 'context' in folder_tgt['dest'] else self._quote(folder_tgt['dest']['context']),
                                    'user':    'False' if not 'user' in folder_tgt['dest'] else self._quote(folder_tgt['dest']['user']),
                                    'group':   'False' if not 'group' in folder_tgt['dest'] else self._quote(folder_tgt['dest']['group']),
                                    'force':   'False' if not 'force' in folder_tgt['dest'] else folder_tgt['dest']['force']
                                }
            
                                # Generate the template method string
                                folder_cmd = self._ftm('deploy_folder', req, opt)
                                template_data['folders'][folder_id] = folder_cmd
                    if not supported:
                        template_data['folders'][folder_id] = _i('# Folder group <%s> not supported on this system' % folder_id)
            
            # System Commands
            if pkey == 'commands':
                for cmd_obj in pobj:
                    cmd_id = cmd_obj['id']
                    indents = get_indent('commands.%s' % cmd_id)
                    supported = False
                    for cmd_tgt in cmd_obj['target']:
                        if self._target_supports(cmd_tgt['supports']):
                            supported = True
                            LOG.info('Parsing and sorting commands object: %s' % cmd_tgt['exec'])
                            commands = ''
                            
                            # Sort the commands and generate the command list
                            cc = 0
                            for key, value in sorted(cmd_tgt['exec'].iteritems(), key=lambda (k,v): (k,v)):
                                commands += _i('worker.run_command("%s", "0")\n' % self._parse_str(value), t=0 if (cc == 0) else indents)
                                cc += 1
                            template_data['commands'][cmd_id] = commands
                    if not supported:
                        template_data['commands'][cmd_id] = _i('# Command group <%s> not supported on this system' % cmd_id)
            
            # User Creation
            if pkey == 'users':
                for user_obj in pobj:
                    user_id    = user_obj['id']
                    
                    # Required arguments
                    req = [self._quote(self._parse_str(user_obj['name']))]

                    # Optional arguments
                    opt = {
                        'group':  'False' if not 'group' in user_obj else self._quote(self._parse_str(user_obj['group'])),
                        'home':   'False' % user_name if not 'home' in user_obj else self._quote(self._parse_str(user_obj['home'])),
                        'pubkey': 'False' if not 'pubkey' in user_obj else self._quote(self._parse_str(user_obj['pubkey'])),
                        'umask':  'False' if not 'umask' in user_obj else self._quote(self._parse_str(user_obj['umask']))
                    }

                    # Generate the template method string
                    user_cmd = self._ftm('deploy_user', req, opt)
                    template_data['users'][user_id] = user_cmd
         
        """ Generate Main Formula Script
        
        Take the object generated above and use it to deploy the main template script.
        """
        td_merged = self.collection.merge_dict(template_data, self.map)
        
        # Main Template
        self._template_to(templates[script_template], self.lws['script'], td_merged)

        # Make the script executable
        os.system('chmod +x %s' % self.lws['script'])

        # Clean up the source code
        try:
            sca = self.r2a(self.lws['script'])
            fca = []
            for l in sca:
                if l.strip():
                    fca.append(l.expandtabs(4))
            fh  = open(self.lws['script'], 'w')
            fh.write(''.join(fca))
            fh.close()
        except Exception as e:
            return invalid(LOG.exception('Encountered exception when formatting formula script: %s' % str(e)))

        # Salt the package
        salt = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(4096))
        sfh  = open('/tmp/%s/.salt' % self.pkg['uuid'], 'w')
        sfh.write(salt)
        sfh.close()

        # Compress the formula package
        compress_cmd = 'tar czf %s -C /tmp %s' % (self.lws['archive'], self.pkg['uuid'])
        LOG.info('Running package compress command: %s' % compress_cmd)
        os.system(compress_cmd)
        
        # Clear the workspace
        shutil.rmtree(self.lws['workspace'])
        
        # Return the package UUID and archive path
        return valid({ 'uuid': self.pkg['uuid'], 'pkg': self.lws['archive'] })