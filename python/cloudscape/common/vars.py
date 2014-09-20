import os
import re
import sys
import platform

# CloudScape Libraries
from cloudscape.common.collection import Collection

"""
Common attributes shared by various CloudScape modules. Defines string
constants, messages, system paths, and other shared information.
"""

# System Type
SYS_TYPE       = platform.system().lower() 

# Normalize Path
def np(p,t=None):
    """
    Helper method used to normalize a path depending on the system type, i.e.
    Linux or Windows.
    
    Normalizing a path for Windows::
    
        # Import the helper method and any required attributes
        from cloudscape.common.vars import np, A_CONF
        
        # Normalize the path, replacing '/' with '\'
        new_path = np(A_CONF)
    
    :param p: The path to normalize
    :type p: str
    :param t: The system type if you want to override the local system type
    :type t: str
    :rtype: str
    """
    if (t=='linux') or (t=='windows'):
        ds = r'\\\\' if t == 'windows' else r'/'
    else:
        ds = r'\\\\' if SYS_TYPE == 'windows' else r'/'
    return re.sub(r'[\/|\\]', ds, p)

# CloudScape User
C_USER         = 'cloudscape'

# Static System Definitions
W_BASE         = 'C:\\CloudScapeAgent'
W_HOME         = '%s\\home' % W_BASE
L_BASE         = '/opt/cloudscape'
L_HOME         = '/home/cloudscape'

# Host types
H_LINUX        = 'linux'
H_WINDOWS      = 'windows'

# Base / Home Directories
C_BASE         = 'C:\\CloudScapeAgent' if (SYS_TYPE == H_WINDOWS) else '/opt/cloudscape'
C_HOME         = W_HOME if (SYS_TYPE == H_WINDOWS) else L_HOME

# CloudScape API Client
C_CLIENT       = np('%s/python/cloudscape/client' % C_BASE)

# Administrator Group / User
G_ADMIN        = '00000000-0000-0000-0000-000000000000'
U_ADMIN        = 'admin'

# Non-privileged Group / Default Group
G_USER         = '11111111-1111-1111-1111-111111111111'
G_DEFAULT      = G_USER

# API Templates
T_ROOT         = '%s/python/cloudscape/engine/templates/api' % C_BASE
T_BASE         = '%s/base' % T_ROOT
T_ACL          = '%s/acl' % T_ROOT

# Agent States
A_INSTALLING   = 'INSTALLING'
A_UNINSTALLING = 'UNINSTALLING'
A_UPDATING     = 'UPDATING'
A_RUNNING      = 'RUNNING'
A_DEPLOYING    = 'DEPLOYING'
A_STOPPED      = 'STOPPED'
A_ERROR        = 'ERROR'

# Formula Run Types
F_INSTALL      = 'install'
F_UNINSTALL    = 'uninstall'
F_UPDATE       = 'update'

# Formula States
F_RUNNING      = 'RUNNING'
F_SUCCESS      = 'SUCCESS'
F_ERROR        = 'ERROR'

# Formula modes
F_MANAGED      = 'managed'
F_UNMANAGED    = 'unmanaged'

# Agent formulas
A_LINUX        = '0f26af78-274f-11e4-983d-0050568406a2'
A_WINDOWS      = '5987cad4-274f-11e4-9b0c-0050568406a2'

# Account types
T_USER         = 'user'
T_HOST         = 'host'

# Formula Types
F_SERVICE      = 'service'
F_UTILITY      = 'utility'
F_GROUP        = 'group'

# Agent commands
A_SYSINFO      = 'sysinfo'
A_EXECPKG      = 'exec-pkg'
A_EXECPY       = 'exec-py'
A_EXECWIN      = 'exec-win'
A_START        = 'start'
A_STOP         = 'stop'
A_RESTART      = 'restart'
A_STATUS       = 'status'

# Agent / Server Configuration
A_CONF         = np('%s/conf/agent.conf' % C_BASE)
S_CONF         = np('%s/conf/server.conf' % C_BASE)
S_CONF_DEF     = np('%s/conf/default/server.conf' % C_BASE)

# Agent Process
A_PID          = '/var/run/cloudscape/agent.pid'
A_CFLAG        = np('%s/.collect' % C_HOME)

# Log Directory
LOG_DIR        = '/var/log/cloudscape' if (SYS_TYPE == H_LINUX) else '%s\\log' % W_HOME

# SSH Paths (Windows)
SSH_DIR        = np('%s/.ssh' % C_HOME)
SSH_HOSTKEY    = np('%s/rsa_host_key' % SSH_DIR)
SSH_AUTHKEYS   = np('%s/authorized_keys' % SSH_DIR)

# Formula paths
FORMULA_DIR    = np('%s/formula' % C_HOME)
FORMULA_LOG    = np('%s/formula' % LOG_DIR)

# Embedded Python paths
PY_BASE        = np('%s/python' % C_BASE)
PY_WRAPPER     = np('%s/python.bat' % PY_BASE)

# Supported operating systems - <distro>/<version>/<arch>
OS_SUPPORTED   = [
    'centos/6/x86_64',
    'ubuntu/12/x86_64',
    'ubuntu/13/x86_64',
    'ubuntu/14/x86_64',
    'windows/8/x86_64',
    'centos/6/i386',
    'ubuntu/12/i386',
    'ubuntu/13/i386',
    'windows/8/x86_64',
    'windows/8/i386',
    'windows/2003server/x86_64',
    'windows/2008server/x86_64',
    'windows/2012server/x86_64',
    'windows/2003server/i386',
    'windows/2008server/i386',
    'windows/2012server/i386'
]
