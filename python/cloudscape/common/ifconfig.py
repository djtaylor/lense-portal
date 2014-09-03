#!/usr/bin/python
import re
import os
import json
import shutil
import platform
from subprocess import Popen, PIPE

# System attributes
SYS_DISTRO = platform.linux_distribution()[0].lower()

# Networking attributes
C_SCRIPTS  = '/etc/sysconfig/network-scripts'
U_CONFIG   = '/etc/network/interfaces'
I_PARENT   = 'parent'
I_ALIAS    = 'alias'

# Alias regular expression
A_REGEX    = re.compile(r'(^[^:]*):(.*$)')

""" Interface IP Alias 

Construct an IP alias object to attach to a parent network interface.
Can be called internally from IFConfig using the 'add_alias' method.
"""
class IPAlias:
    
    """ Initializer """
    def __init__(self, name):
        
        # Subinterface attributes
        self.name      = name
        self.parent    = None
        self.params    = {}
        self.on_boot   = False
        self.bootproto = False
        self.device    = None
        
    """ Attach to Parent """
    def attach(self, parent):
        self.parent = parent
        self.device = '%s:%s' % (self.parent, self.name)

    """ Set Configuration Directive """
    def set_key(self, k, v=None):
        if isinstance(k, str):
            if v:
                self.params[k] = v
        elif isinstance(k, dict):
            for _k, _v in k.iteritems():
                if _v:
                    self.params[_k] = _v
        else:
            raise Exception('Must supply key/value pair or dictionary of key/value pairs')

    """ Construct Configuration """
    def construct(self):
        
        # Ubuntu
        if SYS_DISTRO == 'ubuntu':
            bootstr = 'manual' if not self.on_boot else (self.bootproto)
            iface_obj = {
                'outer': ['iface %s:%s inet %s' % (self.parent, self.name, bootstr)]
            }
            for k,v in self.params.iteritems():
                if not 'inner' in iface_obj:
                    iface_obj['inner'] = {}
                iface_obj['inner'][k] = v
            return iface_obj
        
        # CentOS
        if SYS_DISTRO == 'centos':
            onboot    = 'no' if not self.on_boot else 'yes'
            bootproto = 'none' if (self.bootproto == 'static') else 'dhcp'
            
            # Default parameters if not set manually
            params_def = {
                'NAME':      self.device,
                'DEVICE':    self.device,
                'ONBOOT':    onboot,
                'BOOTPROTO': bootproto
            }
            
            # Construct the interface object
            iface_obj = {}
            for k,v in self.params.iteritems():
                iface_obj[k.upper()] = v
            for k,v in params_def.iteritems():
                if not k in iface_obj:
                    iface_obj[k] = v
            return iface_obj

""" Interface Backup Manager """
class IFBackup:
    
    """ Initializer """
    def __init__(self):
        
        # Configuration files
        self._files = []

    """ Set Backup Target """
    def set_target(self, file):
        if not os.path.isfile(file):
            raise Exception('Target backup file \'%s\' does not exist' % file)
        self._files.append(file)

    """ Clear Backup Targets """
    def clear(self):
        for file in self._files:
            target = '%s.bak' % file
            if os.path.isfile(target):
                try:
                    os.unlink(target)
                except Exception as e:
                    raise Exception('Failed to clear backup file [%s]: %s' % (target, str(e)))

    """ Restore Backup Targets """
    def restore(self):
        for file in self._files:
            source = '%s.bak' % file
            if not os.path.isfile(source):
                raise Exception('Failed to restore file [%s], backup [%s] not found' % (file, source))
            try:
                shutil.copyfile(source, file)
                os.unlink(source)
            except Exception as e:
                raise Exception('Failed to restore file [%s]: %s' % (source, str(e)))
        self.clear()

    """ Save Backup Targets """
    def save(self):
        for file in self._files:
            target = '%s.bak' % file
            try:
                shutil.copyfile(file, target)
            except Exception as e:
                raise Exception('Failed to save configuration backup: [%s] -> [%s]' % (file, target))

""" Linux Interface Configuration """
class IFConfig:
    
    """ Initializer """
    def __init__(self, name):
        
        # Backup manager
        self.backup     = IFBackup()

        # Interface attributes
        self.config     = {}      # Interface configurations
        self.name       = name    # Selected interface name
        self.is_dhcp    = False   # DHCP flag
        self.is_static  = False   # Static IP flag
        self.on_boot    = False   # Boot flag
        self.is_alias   = False   # Interface is an alias
        self.alias_id   = None    # Alias ID, i.e. eth1:<ID>
        self.alias_pa   = None    # Alias parent, i.e. <parent>:1

        # Target interface
        self.iface_set  = []
        self.iface_del  = []

        # Reconstructed configuration
        self.iface_out  = None

        # Parse the configuration
        self._parse_config()
    
    """ Get Configuration """
    def _get_config(self):
        if (self.is_alias) and (SYS_DISTRO == 'ubuntu'):
            return self.config[self.alias_pa]['alias'][self.alias_id]
        else:
            return self.config[self.name]
    
    """ Get Target """
    def _get_target(self, c):
        return c['attrs'] if (SYS_DISTRO == 'centos') else c['attrs']['inner']
                
    """ Delete Configuration Key """
    def _del_key(self, k):
        if k in self._get_target(self._get_config()):
            del _target[k]
    
    """ Set Configuration Key """
    def _set_key(self, k, v):
        self._get_target(self._get_config())[k] = v
    
    """ Run Shell Command """
    def _run_command(self, cmd):
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        o,e  = proc.communicate()
        code = proc.returncode
    
        # Return the code, stdout, and stderr
        return code, o, e
        
    """ Initialize Configuration Object """
    def _config_init(self, name, type, parent=None):
        
        # Parent interface
        if type == 'parent':
            if not name in self.config:
                self.config[name] = {'attrs': {}}
            if not 'attrs' in self.config[name]:
                self.config[name]['attrs'] = {}
                
        # Aliased interface
        if type == 'alias':
            if not parent in self.config:
                self.config[parent] = {'alias': {}}
            
            # Set the interface alias definition
            if not 'alias' in self.config[parent]:
                self.config[parent]['alias'] = {}
            if not name in self.config[parent]['alias']:
                self.config[parent]['alias'][name] = {'attrs': {}}
        
    """ Set Interface Attributes """
    def _set_attrs(self, name, attrs, type, parent=None):
        self._config_init(name, type, parent)
        
        # Base Object
        if_base = None
        if type == 'parent':
            if_base = self.config[name]
        else:
            if_base = self.config[parent]['alias'][name]
        
        # Set the attributes
        for k,v in attrs.iteritems():
            if not k in if_base['attrs']:
                if_base['attrs'][k] = v
            else:
                if isinstance(if_base['attrs'][k], dict):
                    for _k,_v in v.iteritems():
                        if_base['attrs'][k][_k] = _v
                elif isinstance(if_base['attrs'][k], list):
                    if_base['attrs'][k].extend(v)
                else:
                    if_base['attrs'][k] = v
        
    """ Interface Exists """
    def _iface_exists(self, name):
        
        # CentOS
        if SYS_DISTRO == 'centos':
            if name in self.config:
                return True
            return False
        
        # Ubuntu
        if SYS_DISTRO == 'ubuntu':
            _name = name if not (self.is_alias) else self.alias_id
            if _name in self.config:
                return True
            for n,a in self.config.iteritems():
                if 'alias' in a:
                    if _name in a['alias']:
                        return True
            return False
        
    """ Ubuntu: Parse Configuration"""
    def _parse_ubuntu(self, lines):
        
        # Parent / aliased interface flags
        read_iface = False
        read_alias = False
        
        # Current interface name / parent
        if_name    = None
        if_parent  = None
        
        # Parse the network configuration file
        for l in lines:
            if re.match(r'^#.*$', l):
                continue
            
            # Network Interface
            if read_iface:

                # If reading the interface type line
                if re.match(r'^iface[ ]%s.*$' % if_name, l):
                    self._set_attrs(if_name, {'outer': [l.strip()]}, I_PARENT)
                    
                    # Get the boot type
                    if if_name == self.name:
                        bt             = re.compile(r'^.*inet[ ](.*$)').sub(r'\g<1>', l.strip())
                        self.is_dhcp   = False if (bt != 'dhcp') else True
                        self.is_static = False if (bt != 'static') else True
                        self.on_boot   = False if (bt == 'manual') else True
                        
                # If reading the interface attributes
                else:
                    if not l.isspace():
                        l_b = l.strip()
                        l_r = re.compile(r'(^[^ ]*)[ ]*(.*$)')
                        l_k = l_r.sub(r'\g<1>', l_b)
                        l_v = l_r.sub(r'\g<2>', l_b)
                        
                        # Set the attributes
                        self._set_attrs(if_name, {'inner': {l_k:l_v}}, I_PARENT)

            # Network Interface Alias
            if read_alias:
                if not l.isspace():
                    
                    # Extract the interface alias attributes
                    l_b = l.strip()
                    l_r = re.compile(r'(^[^ ]*)[ ]*(.*$)')
                    l_k = l_r.sub(r'\g<1>', l_b)
                    l_v = l_r.sub(r'\g<2>', l_b)
                    
                    # Set the attribute
                    self._set_attrs(if_name, {'inner': {l_k: l_v}}, I_ALIAS, if_parent)

            # If parsing an aliased interface
            if re.match(r'^iface[ ][^:]*:.*$', l) and not read_iface:
                read_alias = True
                s_r        = re.compile(r'^iface[ ]([^:]*):([^ ]*)[ ].*$')
                if_parent  = s_r.sub(r'\g<1>', l).strip()
                if_name    = s_r.sub(r'\g<2>', l).strip()

                # Set the interface attributes
                self._set_attrs(if_name, {'outer': [l.strip()]}, I_ALIAS, if_parent)

            # If parsing a network interface
            if re.match(r'^auto.*$', l):
                read_iface = True
                if_name    = re.compile(r'^auto[ ]*(.*$)').sub(r'\g<1>', l).strip()
                
                # Set the interface attributes
                self._set_attrs(if_name, {'outer': [l.rstrip()]}, I_PARENT)

            # If reading an empty line
            if not l.strip():
                read_iface = False
                read_alias = False

    """ CentOS: Parse Configuration """
    def _parse_centos(self):
        for r,d,f in os.walk(C_SCRIPTS, topdown=False):
            for _f in f:
                _file = '%s/%s' % (r, _f)
                
                # If parsing an interface configuration file
                if 'ifcfg-' in _file:
                    
                    # Backup the file
                    self.backup.set_target(_file)
                    
                    # Get the interface name and extract the configuration
                    ifname = re.compile(r'^ifcfg-(.*$)').sub(r'\g<1>', _f)
                    
                    # If this is an alias
                    if ':' in ifname:
                        parent = re.compile(r'(^[^:]*):.*$').sub(r'\g<1>', ifname)
                        self._config_init(parent, I_PARENT)
                        if not 'alias' in self.config[parent]:
                            self.config[parent]['alias'] = []
                        self.config[parent]['alias'].append(ifname)
                    
                    # Read the configuration file
                    with open(_file) as c:
                        for l in c:
                            
                            # Ignore comments
                            if re.match(r'^#.*$', l):
                                continue
                            
                            # Parse the configuration line
                            l_b = l.strip()
                            l_r = re.compile(r'(^[^=]*)=(.*$)')
                            l_k = l_r.sub(r'\g<1>', l_b)
                            l_v = l_r.sub(r'\g<2>', l_b)
                            
                            # Set attributes
                            self._set_attrs(ifname, {l_k:l_v}, I_PARENT)
                            
                            # Set the boot protocol flag
                            if ifname == self.name:
                                if l_k == 'BOOTPROTO':
                                    self.is_dhcp   = True if ('dhcp' in l_v) else False
                                    self.is_static = True if ('none' in l_v or 'static' in l_v) else False
                                if l_k == 'ONBOOT':
                                    self.on_boot   = True if ('yes' in l_v) else False
            
    """ Ubuntu: Reconstruct Configuration """
    def _reconstruct_ubuntu(self):
        c = 0
        self.iface_out = ''
        for i,o in self.config.iteritems():
            if c != 0:
                self.iface_out += '\n'
            for l in o['attrs']['outer']:
                self.iface_out += '%s\n' % l
            if 'inner' in o['attrs']:
                for k,v in o['attrs']['inner'].iteritems():
                    self.iface_out += '    %s %s\n' % (k,v)
            if 'alias' in o:
                for i,a in o['alias'].iteritems():
                    for l in a['attrs']['outer']:
                        self.iface_out += '\n%s\n' % l
                    if 'inner' in a['attrs']:
                        for k,v in a['attrs']['inner'].iteritems():
                            self.iface_out += '    %s %s\n' % (k,v)
            c += 1
    
    """ CentOS: Reconstruct Configuration """
    def _reconstruct_centos(self):
        self.iface_out = {}
        for name,obj in self.config.iteritems():
            self.iface_out[name] = ''
            c = 0
            for k,v in obj['attrs'].iteritems():
                p = '' if (c == 0) else '\n'
                self.iface_out[name] += '%s%s=%s' % (p,k,v)
                c += 1

    """ Parse Configuration """
    def _parse_config(self):
        if ':' in self.name:
            self.is_alias = True
            self.alias_pa = A_REGEX.sub(r'\g<1>', self.name)
            self.alias_id = A_REGEX.sub(r'\g<2>', self.name)

        # Ubuntu
        if SYS_DISTRO == 'ubuntu':
            self.backup.set_target(U_CONFIG)
            with open(U_CONFIG, 'r') as f:
                self._parse_ubuntu(f.readlines())

        # CentOS
        if SYS_DISTRO == 'centos':
            self._parse_centos()

        # If the selected interface was not found
        if not self._iface_exists(self.name):
            raise Exception('Interface %s not configured on the local system' % self.name)

    """ Reconsruct Configuration """
    def _reconstruct_config(self):
        _rmap = {
            'ubuntu': self._reconstruct_ubuntu,
            'centos': self._reconstruct_centos
        }
        
        # Reconstruct the configuration
        try:
            _rmap[SYS_DISTRO]()
        except Exception as e:
            raise Exception('Failed to reconstruct the configuration: %s' % str(e))

    """ Clear Configuration """
    def clear(self):
        obj = {
            'iface': {
                'config': {}
            }
        }

    """ Remove Interface IP Alias """
    def remove_alias(self, name):
        if name in self.config[self.name]['alias']:
            del self.config[self.name]['alias'][name]
            self.iface_del.append('%s:%s' % (self.name, name))
            
    """ Add Interface IP Alias """
    def add_alias(self, name, params={}, onboot=True, static=False, auto_up=True):
        
        # Add the new interface
        alias = IPAlias(name)
        alias.attach(self.name)
        alias.set_key(params)
        alias.on_boot = onboot
        alias.bootproto = 'static' if static else 'dhcp'
        
        # Flag the alias for loading
        if auto_up:
            self.iface_set.append(alias.device)
        
        # Construct the interface
        if SYS_DISTRO == 'ubuntu':
            if not 'alias' in self.config[self.name]:
                self.config[self.name]['alias'] = {}
            
            if name in self.config[self.name]['alias']:
                raise Exception('Subinterface %s already exists for %s' % (alias.device, self.name))
            self.config[self.name]['alias'][name] = { 'attrs': alias.construct()}
        if SYS_DISTRO == 'centos':
            if name in self.config:
                raise Exception('Subinterface %s already exists for %s' % (alias.device, self.name))
            self.config[alias.device] = {'attrs': alias.construct()}

    """ Command: ifdown """
    def _ifdown(self, name):
        c,o,e = self._run_command(['ifdown', name])
        
        # Make sure the interface was brought down
        if c != 0:
            self.backup.restore()
            _c,_o,_e = self._run_command(['ifup', name])
            if _c != 0:
                raise Exception('Failed to restore configuration: %s' % str(_e))
            raise Exception('Failed to set configuration: %s' % str(e))

    """ Command: ifup """
    def _ifup(self, name):
        c,o,e = self._run_command(['ifup', name])
        
        # Make sure the interface was brought down
        if c != 0:
            self.backup.restore()
            _c,_o,_e = self._run_command(['ifup', name])
            if _c != 0:
                raise Exception('Failed to restore configuration: %s' % str(_e))
            raise Exception('Failed to set configuration: %s' % str(e))

    """ Remove Interface """
    def remove(self):
        
        # Ubuntu
        if SYS_DISTRO == 'ubuntu':
            
            # If removing an alias
            if self.is_alias:
                del self.config[self.alias_pa]['alias'][self.alias_id]
                
            # If removing a physical adapter
            else:
            
                # Get rid of aliases first
                if 'alias' in self.config[self.name]:
                    for ak,ao in self.config[self.name]['alias'].iteritems():
                        _iface = '%s:%s' % (self.name, ak)
                        self._ifdown(_iface)
                    del self.config[self.name]['alias']
        
                # Delete the main interface
                del self.config[self.name]
            
            # Bring down the main interface and write the config
            self._ifdown(self.name)
            self._write_config()
        
        # CentOS
        if SYS_DISTRO == 'centos':
            
            # Get rid of aliases first
            if 'alias' in self.config[self.name]:
                for ak in self.config[self.name]['alias']:
                    self._ifdown(ak)
                    os.unlink('%s/ifcfg-%s' % (C_SCRIPTS, ak))
            
            # Delete the main interface
            self._ifdown(self.name)
            os.unlink('%s/ifcfg-%s' % (C_SCRIPTS, self.name))

    """ Set Configuration Directives """
    def set_key(self, k, v=None):
        if isinstance(k, str):
            if v:
                self._set_key(k, v)
        elif isinstance(k, dict):
            for _k, _v in k.iteritems():
                if _v:
                    self._set_key(_k, _v)
        else:
            raise Exception('Argument must be either key/value, or a dictionary of key/values')

        # Only reload the interface if actually making changes
        self.iface_set.append(self.name)

    """ Remove Configuration Directives """
    def remove_key(self, d):
        if isinstance(d, str):
            self._del_key(d)
        elif isinstance(d, list):
            for i in d:
                self._del_key(i)
        else:
            raise Exception('Argument must be a string or list')

    """ Write Configuration """
    def _write_config(self):
        self._reconstruct_config()
        
        # Write out the configuration
        try:
            
            # Ubuntu
            if SYS_DISTRO == 'ubuntu':
                for f in self.iface_del:
                    self._ifdown(f)
                with open(U_CONFIG, 'w') as f:
                    f.write(self.iface_out)
            
            # CentOS
            if SYS_DISTRO == 'centos':
                for f in self.iface_set:
                    _file = '%s/ifcfg-%s' % (C_SCRIPTS, f)
                    with open(_file, 'w') as _f:
                        _f.write(self.iface_out[f])
                for f in self.iface_del:
                    _file = '%s/ifcfg-%s' % (C_SCRIPTS, f)
                    self._ifdown(f)
                    os.unlink(_file) 
        except Exception as e:
            self.backup.restore()
            raise Exception('Failed to write new configuration: %s' % str(e))

    """ Reload Configuration """
    def _reload_config(self):
        for iface in self.iface_set:
            self._ifdown(iface)
            self._ifup(iface)

    """ Apply Configuration """
    def apply(self):
        
        # Backup the configuration
        self.backup.save()

        # Update the configuration file
        self._write_config()
        
        # Reload the interface configuration
        self._reload_config()
        
        # Clear the backup
        self.backup.clear()