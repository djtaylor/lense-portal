import re
import os
import json
from uuid import uuid4

# Django Libraries
from django.core.serializers.json import DjangoJSONEncoder

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid, mod_has_class
from cloudscape.engine.api.auth.token import APIToken
from cloudscape.common.vars import T_ACL, C_BASE
from cloudscape.engine.api.app.auth.models import DBAuthACLKeys, DBAuthACLEndpointsGlobal, \
                                                  DBAuthACLEndpointsHost, DBAuthACLEndpointsObject, \
                                                  DBAuthEndpoints, DBAuthACLObjects

class AuthEndpointsDelete:
    """
    Delete a new API endpoint.
    """
    def __init__(self, parent):
        self.api = parent

        # Target endpoint
        self.endpoint = self.api.data['uuid']

    def launch(self):
        """
        Worker method used for deleting an endpoint.
        """
        
        # Make sure the endpoint exists
        if not DBAuthEndpoints.objects.filter(uuid=self.endpoint).count():
            return invalid(self.api.log.error('Could not delete endpoint [%s], not found in database' % self.endpoint))
        
        # Get the endpoint details
        endpoint_row = DBAuthEndpoints.objects.filter(uuid=self.endpoint).values()[0]
        
        # Make sure the endpoint isn't protected
        if endpoint_row['protected']:
            return invalid('Cannot delete a protected endpoint')
        
        # Delete the endpoint
        try:
            DBAuthEndpoints.objects.filter(uuid=self.endpoint).delete()
        except Exception as e:
            return invalid(self.api.log.exeption('Failed to delete endpoint: %s' % str(e)))
        
        # Construct and return the web data
        web_data = {
            'uuid': self.endpoint
        }
        return valid('Successfully deleted endpoint', web_data)

class AuthEndpointsCreate:
    """
    Create a new API endpoint.
    """
    def __init__(self, parent):
        self.api  = parent

    def launch(self):
        """
        Worker method for creating a new endpoint.
        """
        
        # Concatenate the path and action to the name
        ep_name      = '%s/%s' % (self.api.data['path'], self.api.data['action'])
        ep_desc      = self.api.data['desc']
        ep_path      = self.api.data['path']
        ep_action    = self.api.data['action']
        ep_method    = self.api.data['method']
        ep_class     = self.api.data['cls']
        ep_mod       = self.api.data['mod']
        ep_utils     = '[]' if not ('utils' in self.api.data) else self.api.data['utils']
        ep_uuid      = str(uuid4())
        ep_protected = self.api.data['protected']
        ep_enabled   = self.api.data['enabled']
        ep_object    = None if not ('object' in self.api.data) else self.api.data['object']
        ep_obj_key   = None if not ('object_key' in self.api.data) else self.api.data['object_key']
        ep_rmap      = json.dumps({
            '_type': 'dict',
            '_required': [],
            '_optional': ['_data']                 
        })
        
        # Make sure the name isn't taken already
        if DBAuthEndpoints.objects.filter(name=ep_name).count():
            return invalid('The endpoint [%s] already exists, please use a different <path>/<action> combination' % ep_name)
        
        # Try to import the module and make sure it contains the class definition
        mod_status = mod_has_class(ep_mod, ep_class)
        if not mod_status['valid']:
            return mod_status
        
        # Save the endpoint
        try:
            
            endpoint = DBAuthEndpoints(
                uuid       = ep_uuid,
                name       = ep_name,
                desc       = ep_desc,
                path       = ep_path,
                action     = ep_action,
                method     = ep_method,
                mod        = ep_mod,
                cls        = ep_class,
                utils      = ep_utils,
                rmap       = ep_rmap,
                protected  = ep_protected,
                enabled    = ep_enabled,
                object     = ep_object,
                object_key = ep_obj_key,
                locked     = False,
                locked_by  = None
            )
            endpoint.save()
            
            # Construct and return web data
            web_data = {
                'uuid': ep_uuid,
                'name': ep_name,
                'path': ep_path,
                'action': ep_action,
                'method': ep_method,
                'desc': ep_desc,
                'enabled': ep_enabled,
                'protected': ep_protected
            }
            return valid('Successfully created endpoint', web_data)
            
        # Failed to save endpoint
        except Exception as e:
            return invalid('Failed to create endpoint: %s' % str(e))

class AuthEndpointsSave:
    """
    Save changes to an endpoint.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target endpoint
        self.endpoint = self.api.data['uuid']

    def launch(self):
        """
        Worker method for saving changes to an endpoint.
        """

        # Make sure the endpoint exists
        if not DBAuthEndpoints.objects.filter(uuid=self.endpoint).count():
            return invalid(self.api.log.error('Could not save endpoint [%s], not found in database' % self.endpoint))

        # Validate the endpoint attributes
        #ep_status = self.api.util.AuthEndpointsValidate.launch()
        #if not ep_status['valid']:
        #    return ep_status

        # Get the endpoint details
        endpoint_row = DBAuthEndpoints.objects.filter(uuid=self.endpoint).values()[0]
    
        # Default values
        path       = endpoint_row['path'] if not ('path' in self.api.data) else self.api.data['path']
        action     = endpoint_row['action'] if not ('action' in self.api.data) else self.api.data['action']
        method     = endpoint_row['method'] if not ('method' in self.api.data) else self.api.data['method']
        enabled    = endpoint_row['enabled'] if not ('enabled' in self.api.data) else self.api.data['enabled']
        mod        = endpoint_row['mod'] if not ('mod' in self.api.data) else self.api.data['mod']
        cls        = endpoint_row['cls'] if not ('cls' in self.api.data) else self.api.data['cls']
        utils      = endpoint_row['utils'] if not ('utils' in self.api.data) else self.api.data['utils']
        rmap       = endpoint_row['rmap'] if not ('rmap' in self.api.data) else self.api.data['rmap']
        protected  = endpoint_row['protected'] if not ('protected' in self.api.data) else self.api.data['protected']
        object     = endpoint_row['object'] if not ('object' in self.api.data) else self.api.data['object']
        object_key = endpoint_row['object_key'] if not ('object_key' in self.api.data) else self.api.data['object_key']
        name       = '%s/%s' % (path, action)

        # Attempt to update the endpoint
        try:
            DBAuthEndpoints.objects.filter(uuid=self.endpoint).update(
                name       = name,
                path       = path,
                action     = action,
                method     = method,
                enabled    = enabled,
                mod        = mod,
                cls        = cls,
                utils      = json.dumps(utils),
                protected  = protected,
                object     = object,
                object_key = object_key,
                rmap       = rmap
            )
            return valid('Successfully updated endpoint.')
        except Exception as e:
            return invalid(self.api.log.exception('Failed to update endpoint: %s' % str(e)))

class AuthEndpointsValidate:
    """
    Validate changes to an endpoint prior to saving.
    """
    def __init__(self, parent):
        self.api = parent

        # Target endpoint
        self.endpoint = self.api.data['uuid']

    def _validate(self):
        """
        Validate the endpoint attributes.
        """
    
        # Get all endpoints
        endpoint_all = DBAuthEndpoints.objects.all().values()
    
        # ACL objects
        acl_objects  = list(DBAuthACLObjects.objects.all().values())
    
        # Construct available endpoint utilities
        endpoint_utils = []
        for ep in endpoint_all:
            endpoint_utils.append('%s.%s' % (ep['mod'], ep['cls']))
    
        # Get the endpoint details
        endpoint_row = DBAuthEndpoints.objects.filter(uuid=self.endpoint).values()[0]
    
        # Default values
        path       = endpoint_row['path'] if not ('path' in self.api.data) else self.api.data['path']
        action     = endpoint_row['action'] if not ('action' in self.api.data) else self.api.data['action']
        method     = endpoint_row['method'] if not ('method' in self.api.data) else self.api.data['method']
        enabled    = endpoint_row['enabled'] if not ('enabled' in self.api.data) else self.api.data['enabled']
        protected  = endpoint_row['protected'] if not ('protected' in self.api.data) else self.api.data['protected']
        mod        = endpoint_row['mod'] if not ('mod' in self.api.data) else self.api.data['mod']
        cls        = endpoint_row['cls'] if not ('cls' in self.api.data) else self.api.data['cls']
        utils      = endpoint_row['utils'] if not ('utils' in self.api.data) else self.api.data['utils']
        rmap       = endpoint_row['rmap'] if not ('rmap' in self.api.data) else self.api.data['rmap']
        object     = endpoint_row['object'] if not ('object' in self.api.data) else self.api.data['object']
        object_key = endpoint_row['object_key'] if not ('object_key' in self.api.data) else self.api.data['object_key']
    
        # Make sure the path and action strings are valid
        if not re.match(r'^[a-z0-9][a-z0-9\/]*[a-z0-9]$', path):
            return invalid('Failed to validate endpoint [%s], invalid <path> value: %s' % (self.endpoint, path))
        if not re.match(r'^[a-z]*$', action):
            return invalid('Failed to validate endpoint [%s], invalid <action> value: %s' % (self.endpoint, action))
    
        # Make sure the method is valid
        if not method in ['GET', 'POST', 'PUT', 'DELETE']:
            return invalid('Failed to validate endpoint [%s], invalid <method> value: %s' % (self.endpoint, method))
    
        # Make sure the object type is supported
        obj_supported = False if object else True
        for acl_obj in acl_objects:
            if acl_obj['type'] == object:
                obj_supported = True
                break
        if not obj_supported:
            return invalid('Failed to validate endpoint, using unsupported endpoint object type [%s]' % object)
    
        # Make sure the request map is valid JSON
        try:
            tmp = json.loads(rmap)
        except Exception as e:
            return invalid('Failed to validate request map JSON: %s' % str(e))
    
        # Validate the module
        mod_path = mod.replace('.', '/')
        if not os.path.isfile('%s/python/%s.py' % (C_BASE, mod_path)):
            return invalid('Failed to validate endpoint [%s], module [%s] not found' % (self.endpoint, mod))
    
        # Validate the class
        mod_status = mod_has_class(mod, cls)
        if not mod_status['valid']:
            return mod_status
    
        # Validate external utilities
        for util in utils:
            if not util in endpoint_utils:
                return invalid('Failed to validate endpoint [%s], could not locate external utility class [%s]' % (self.endpoint, util))
    
        # Map object
        self.epattr = {
            'name':      '%s/%s' % (path, action),
            'path':      path,
            'action':    action,
            'method':    method,
            'enabled':   enabled,
            'protected': protected,
            'mod':       mod,
            'cls':       cls,
            'utils':     utils
        }
        
        # Attributes constructed
        return valid()

    def launch(self):
        """
        Worker method for validating endpoint changes.
        """
        
        # Make sure the endpoint exists
        if not DBAuthEndpoints.objects.filter(uuid=self.endpoint).count():
            return invalid(self.api.log.error('Could not validate endpoint [%s], not found in database' % self.endpoint))

        # Validate the endpoint attributes
        ep_status = self._validate()
        if not ep_status['valid']:
            return ep_status
        
        # Endpoint is valid
        return valid('Endpoint validation succeeded.')

class AuthEndpointsClose:
    """
    Close an endpoint and release the editing lock.
    """
    def __init__(self, parent):
        self.api = parent

        # Target endpoint
        self.endpoint = self.api.data['uuid']

    def launch(self):
        """
        Worker method for closing an endpoint and releasing the editing lock.
        """
    
        # Make sure the endpoint exists
        if not DBAuthEndpoints.objects.filter(uuid=self.endpoint).count():
            return invalid(self.api.log.error('Could not check in endpoint [%s], not found in database' % self.endpoint))
        
        # Get the endpoint details row
        endpoint_row = DBAuthEndpoints.objects.filter(uuid=self.endpoint).values()[0]
        
        # Check if the endpoint is already checked out
        if endpoint_row['locked'] == False:
            return invalid(self.api.log.error('Could not check in endpoint [%s], already checked in' % self.endpoint))
        
        # Unlock the endpoint
        self.api.log.info('Checked in endpoint [%s] by user [%s]' % (self.endpoint, self.api.user))
        try:
            DBAuthEndpoints.objects.filter(uuid=self.endpoint).update(
                locked    = False,
                locked_by = None
            )
            return valid('Successfully checked in endpoint')
            
        # Failed to check out the formula
        except Exception as e:
            return invalid(self.api.log.error('Failed to check in endpoint with error: %s' % str(e)))

class AuthEndpointsOpen:
    """
    Open an endpoint for editing.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target endpoint
        self.endpoint = self.api.data['uuid']
        
    def launch(self):
        """
        Worker method to open the endpoint for editing.
        """
        self.api.log.info('Preparing to checkout endpoint [%s] for editing' % self.endpoint)
    
        # Make sure the endpoint exists
        if not DBAuthEndpoints.objects.filter(uuid=self.endpoint).count():
            return invalid(self.api.log.error('Could not open endpoint [%s] for editing, not found in database' % self.endpoint))
        
        # Get the endpoint details row
        endpoint_row = DBAuthEndpoints.objects.filter(uuid=self.endpoint).values()[0]
        
        # Check if the endpoint is locked
        if endpoint_row['locked'] == True:
            self.api.log.info('Endpoint \'%s\' already checked out by user \'%s\'' % (self.endpoint, endpoint_row['locked_by']))
            
            # If the formula is checked out by the current user
            if endpoint_row['locked_by'] == self.api.user:
                self.api.log.info('Endpoint checkout request OK, requestor \'%s\' is the same as the locking user \'%s\'' % (self.api.user, endpoint_row['locked_by']))
                return valid('Endpoint already checked out by the current user')
            else:
                return invalid(self.api.log.error('Could not open endpoint [%s] for editing, already checked out by %s' % (self.endpoint, formula_row['locked_by'])))
    
        # Set the locking user
        locked_by = self.api.user
        
        # Lock the endpoint for editing
        self.api.log.info('Checkout out endpoint \'%s\' for editing by user \'%s\'' % (self.endpoint, locked_by))
        try:
            DBAuthEndpoints.objects.filter(uuid=self.endpoint).update(
                locked    = True,
                locked_by = self.api.user
            )
            return valid('Successfully checked out endpoint for editing')
            
        # Failed to check out the formula
        except Exception as e:
            return invalid(self.api.log.error('Failed to check out endpoint for editing with error: %s' % str(e)))
        

class AuthEndpointsGet:
    """
    Retrieve a listing of API endpoints.
    """
    def __init__(self, parent):
        self.api = parent
        
    def launch(self):
        """
        Worker method to retrieve a listing of API endpoints.
        """
        try:
            
            # If grabbing a specific endpoint
            if 'uuid' in self.api.data:
                
                # If the endpoint doesn't exist
                if not DBAuthEndpoints.objects.filter(uuid=self.api.data['uuid']).count():
                    return invalid('Endpoint [%s] does not exist' % self.api.data['uuid'])
                return valid(json.dumps(DBAuthEndpoints.objects.filter(uuid=self.api.data['uuid']).values()[0]))
                
            # Return all endpoints
            else:
                return valid(json.dumps(list(DBAuthEndpoints.objects.all().values())))
        except Exception as e:
            return invalid(self.api.log.exception('Failed to retrieve endpoints listing: %s' % str(e)))

class AuthACLObjectsDelete:
    """
    Delete an existing ACL object definition.
    """
    def __init__(self, parent):
        self.api  = parent
        
        # Get the target ACL object
        self.type = self.api.get_data('type')

    def launch(self):
        """
        Worker method for deleting an ACL object definition.
        """
        
        # If the ACL object doesn't exist
        if not DBAuthACLObjects.objects.filter(type=self.type).count():
            return invalid('Cannot delete ACL object [%s], not found in database' % self.type)
        self.api.log.info('BLARGLE')
        
        # Get the ACL object definition
        acl_object = DBAuthACLObjects.objects.filter(type=self.type).values(detailed=True)[0]
        
        # If the ACL object has any assigned object
        if acl_object['objects']:
            return invalid('Cannot delete ACL object [%s] definition, contains [%s] child objects' % (self.type, str(len(acl_object['objects']))))

        # Delete the ACL object definition
        try:
            DBAuthACLObjects.objects.filter(type=self.type).delete()
            
        # Critical error when deleting ACL object
        except Exception as e:
            return invalid(self.api.log.exception('Failed to delete ACL object [%s] definition: %s' % (self.type, str(e))))

        # Return the response
        return valid('Successfully deleted ACL object definition', {
            'type': self.type
        })

class AuthACLObjectsCreate:
    """
    Create a new ACL object definition.
    """
    def __init__(self, parent):
        self.api  = parent
        
        # API object attributes
        self.attr = self._set_attr()
        
    def _set_attr(self):
        """
        Set the attributes for the new ACL object.
        """
        
        # Attribute keys
        attr_keys = [
            'type', 
            'name', 
            'acl_mod', 
            'acl_cls', 
            'acl_key', 
            'obj_mod', 
            'obj_cls', 
            'obj_key'
        ]
        
        # Construct and return the attributes object
        return {k:self.api.get_data(k) for k in attr_keys}
        
    def launch(self):
        """
        Worker method for creating a new ACL object definition.
        """
        
        # Make sure the type definition is not already used
        if DBAuthACLObjects.objects.filter(type=self.attr['type']).count():
            return invalid('Failed to create ACL object type [%s], already defined' % self.attr['type'])
        
        # Check the ACL and object module/class definitions
        for key,status in {
            'acl': mod_has_class(self.attr['acl_mod'], self.attr['acl_cls'], no_launch=True),
            'obj': mod_has_class(self.attr['obj_mod'], self.attr['obj_cls'], no_launch=True)
        }.iteritems():
            if not status['valid']:
                return status
        
        # If a default ACL UUID is supplied
        if ('def_acl' in self.api.data):
            if not DBAuthACLKeys.objects.filter(uuid=self.attr['def_acl']).count():
                return invalid('Failed to create ACL object type [%s], default ACL [%s] not found' % (self.attr['type'], self.attr['def_acl']))
        
            # Get the default ACL object
            self.attr['def_acl'] = DBAuthACLKeys.objects.get(uuid=self.api.data['def_acl'])
            
            # Make sure the ACL has object type authentication enabled
            if not self.attr['def_acl']['type_object']:
                return invalid('Failed to create ACL object type [%s], default ACL [%s] must have object authentication enabled' % (self.attr['type'], self.attr['def_acl']['uuid']))
        
        # Create the ACL object definition
        try:
            DBAuthACLObjects(**self.attr).save()
            
        # Critical error when saving ACL object definition
        except Exception as e:
            return invalid(self.api.log.exception('Failed to create ACL object type [%s]: %s' % (self.attr['type'], str(e))))
        
        # Return the response
        return valid('Successfully created ACL object definition', {
            'type': self.attr['type'],
            'name': self.attr['name']
        })

class AuthACLObjectsUpdate:
    """
    Update attributes for an ACL object.
    """
    def __init__(self, parent): 
        self.api = parent

        # Target object type
        self.type = self.api.get_data('type')

    def launch(self):
        """
        Worker method for updating an ACL object.
        """
        
        # Make sure the object definition exists
        if not DBAuthACLObjects.objects.filter(type=self.type).count():
            return invalid('Failed to update ACL object, type definition [%s] not found' % self.type)
        
        # Get the existing ACL object definition
        acl_obj = DBAuthACLObjects.objects.filter(type=self.type).values()[0]
        
        # ACL module / class
        acl_mod = acl_obj['acl_mod'] if not ('acl_mod' in self.api.data) else self.api.data['acl_mod']
        acl_cls = acl_obj['acl_cls'] if not ('acl_cls' in self.api.data) else self.api.data['acl_cls']
        
        # Make sure the module/class combination is valid
        acl_mod_status = mod_has_class(acl_mod, acl_cls, no_launch=True)
        if not acl_mod_status['valid']:
            return acl_mod_status
        
        # Object module / class
        obj_mod = acl_obj['obj_mod'] if not ('obj_mod' in self.api.data) else self.api.data['obj_mod']
        obj_cls = acl_obj['obj_cls'] if not ('obj_cls' in self.api.data) else self.api.data['obj_cls']
        
        # Make sure the module/class combination is valid
        obj_mod_status = mod_has_class(obj_mod, obj_cls, no_launch=True)
        if not obj_mod_status['valid']:
            return obj_mod_status
        
        # If updating the default ACL definition
        def_acl = None
        if 'def_acl' in self.api.data:
            
            # Make sure the default ACL exists
            if not DBAuthACLKeys.objects.filter(uuid=self.api.data['def_acl']).count():
                return invalid('Failed to update ACL object type [%s], default ACL [%s] not found' % (self.type, self.api.data['def_acl']))
        
            # Get the default ACL object
            def_acl = DBAuthACLKeys.objects.get(uuid=self.api.data['def_acl'])
            
            # Make sure the ACL has object type authentication enabled
            if not def_acl.type_object:
                return invalid('Failed to update ACL object type [%s], default ACL [%s] must have object authentication enabled' % (self.type, def_acl.uuid))
        
            # Clear the UUID string from the API data
            del self.api.data['def_acl']
        
        # Update the object definition
        try:
            
            # Update string values
            DBAuthACLObjects.objects.filter(type=self.type).update(**self.api.data)
            
            # If changing the default ACL
            if def_acl:
                acl_obj = DBAuthACLObjects.objects.get(type=self.type)
                acl_obj.def_acl = def_acl
                acl_obj.save()
        
        # Critical error when updating ACL object definition
        except Exception as e:
            return invalid('Failed to update ACL object: %s' % str(e))
         
        # Successfully updated object
        return valid('Successfully updated ACL object')

class AuthACLObjectsGet:
    """
    Retrieve a list of supported ACL object types.
    """
    def __init__(self, parent):
        self.api      = parent

        # Type filter / detailed return
        self.type     = self.api.get_data('type')
        self.detailed = self.api.get_data('detailed')

        # Extract all ACL objects
        self.objects  = list(DBAuthACLObjects.objects.all().values(detailed=self.detailed))

    def launch(self):
        """
        Worker method for returning a list of ACL object types.
        """
        
        # If retrieving a specific object type
        if self.type:
            object_details = [x for x in self.objects if x['type'] == self.type]
            
            # Make sure the object type exists
            if not object_details:
                return invalid('Could not locate ACL object of type [%s] in the database' % self.type)
            
            # Return the ACL object
            return valid(object_details[0])
        
        # Retrieving all ACL object definitions
        else:
            
            # Return ACL object definitions
            return valid(self.objects)
     
class AuthACLUpdate:
    """
    Update an existing ACL definition.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target ACL
        self.acl = self.api.data['uuid']
        
    def launch(self):
        """
        Worker method for updating an existing ACL definition.
        """
        
        # Make sure the ACL exists
        if not DBAuthACLKeys.objects.filter(uuid=self.acl).count():
            return invalid('Failed to update ACL [%s], not found in database' % self.acl)
        
        # Get the ACL details
        acl_row  = DBAuthACLKeys.objects.filter(uuid=self.acl).values()[0]
        
        # ACL attributes
        acl_name   = acl_row['name'] if not ('name' in self.api.data) else self.api.data['name']
        acl_desc   = acl_row['desc'] if not ('desc' in self.api.data) else self.api.data['desc']
        acl_global = acl_row['type_global'] if not ('type_global' in self.api.data) else self.api.data['type_global']
        acl_object = acl_row['type_object'] if not ('type_object' in self.api.data) else self.api.data['type_object']
        acl_host   = acl_row['type_host'] if not ('type_host' in self.api.data) else self.api.data['type_host']
        
        # Update ACL details
        try:
            DBAuthACLKeys.objects.filter(uuid=self.acl).update(
                name        = acl_name,
                desc        = acl_desc,
                type_object = acl_object,
                type_global = acl_global,
                type_host   = acl_host                                         
            )
            self.api.log.info('Updated properties for ACL [%s]' % self.acl)
        except Exception as e:
            return invalid(self.api.log.exception('Failed to update details for ACL [%s]: %s' % (self.acl, str(e))))
        
        # If updating ACL endpoints
        if 'endpoints' in self.api.data:
            endpoints     = self.api.data['endpoints']
            
            # Get all endpoints
            endpoints_all = list(DBAuthEndpoints.objects.all().values())
            
            # Only support one object type per ACL object access definition
            if 'object' in endpoints:
                obj_last = None
                for endpoint in endpoints_all:
                    if (endpoint['uuid'] in endpoints['object']) and (endpoint['object']):
                        if (obj_last == None) or (obj_last == endpoint['object']):
                            obj_last = endpoint['object']
                        else:
                            return invalid('Object type mismatch <%s -> %s>, ACLs only support one object type per definition.' % (obj_last, endpoint['object']))
            
            # Get the current ACL object
            acl_obj = DBAuthACLKeys.objects.get(uuid=self.acl)
            
            # Update ACL endpoints
            for acl_type, acl_ep in endpoints.iteritems():
                self.api.log.info('Updating access type [%s] for ACL [%s]' % (acl_type, self.acl))
                try:
                    
                    # Global
                    if acl_type == 'global':
                        
                        # Clear old definitions
                        DBAuthACLEndpointsGlobal.objects.filter(acl=self.acl).delete()
                        
                        # Put in new definitions
                        for endpoint in acl_ep:
                            ep_obj = DBAuthACLEndpointsGlobal(
                                acl      = acl_obj,
                                endpoint = DBAuthEndpoints.objects.get(uuid=endpoint)
                            )
                            ep_obj.save()
                    
                    # Object
                    if acl_type == 'object':
                        
                        # Clear old definitions
                        DBAuthACLEndpointsObject.objects.filter(acl=self.acl).delete()
                        
                        # Put in new definitions
                        for endpoint in acl_ep:
                            ep_obj = DBAuthACLEndpointsObject(
                                acl      = acl_obj,
                                endpoint = DBAuthEndpoints.objects.get(uuid=endpoint)
                            )
                            ep_obj.save()
                    
                    # Host
                    if acl_type == 'host':
                        
                        # Clear old definitions
                        DBAuthACLEndpointsHost.objects.filter(acl=self.acl).delete()
                        
                        # Put in new definitions
                        for endpoint in acl_ep:
                            ep_obj = DBAuthACLEndpointsHost(
                                acl      = acl_obj,
                                endpoint = DBAuthEndpoints.objects.get(uuid=endpoint)
                            )
                            ep_obj.save()
                    
                    # All endpoints updated
                    self.api.log.info('Updated all endpoints for ACL [%s]' % self.acl)
                    
                # Failed to update endpoints
                except Exception as e:
                    return invalid(self.api.log.exception('Failed to update [%s] endpoints for ACL [%s]: %s' % (acl_type, self.acl, str(e))))
        
        # ACL updated
        return valid('Succesfully updated ACL')
        
class AuthACLDelete:
    """
    Delete an existing ACL.
    """            
    def __init__(self, parent):
        self.api = parent
        
        # Target ACL
        self.acl = self.api.data['uuid']
        
    def launch(self):
        """
        Worker method for deleting an existing ACL.
        """
        
        # Make sure the ACL exists
        if not DBAuthACLKeys.objects.filter(uuid=self.acl).count():
            return invalid('Failed to delete ACL [%s], not found in database' % self.acl)
        
        # Delete the ACL definition
        try:
            DBAuthACLKeys.objects.filter(uuid=self.acl).delete()
            self.api.log.info('Deleted ACL definition [%s]' % self.acl)
            
            # ACL deleted
            return valid('Successfully deleted ACL', {
                'uuid': self.acl
            })
            
        # Failed to delete ACL
        except Exception as e:
            return invalid(self.api.log.exception('Failed to delete ACL [%s]: %s' % (self.acl, str(e))))
        
class AuthACLCreate:
    """
    Create a new ACL definition.
    """
    def __init__(self, parent):
        self.api = parent
        
    def launch(self):
        """
        Worker method for handling ACL definition creation.
        """
        
        # Generate a UUID for the ACL
        acl_uuid = str(uuid4())
        
        # ACL attributes
        acl_name = self.api.data['name']
        acl_desc = self.api.data['desc']
        acl_type = self.api.data['type']
        acl_eps  = self.api.data['endpoints']
        
        # Make sure the ACL doesn't exist
        if DBAuthACLKeys.objects.filter(name=acl_name).count():
            return invalid('ACL [%s] is already defined' % acl_name)

        # Create the ACL key entry
        try:
            acl_key = DBAuthACLKeys(
                uuid        = acl_uuid,
                name        = acl_name,
                desc        = acl_desc,
                type_object = True if ('object' in acl_type) else False,
                type_global = True if ('global' in acl_type) else False,
                type_host   = True if ('host' in acl_type) else False
            )
            acl_key.save()
        except Exception as e:
            return invalid(self.api.log.exception('Failed to create ACL definition: %s' % str(e)))
            
        # Create ACL definition
        return valid('Create new ACL definition', {
            'uuid': acl_uuid,
            'name': acl_name,
            'desc': acl_desc
        })

class AuthACLGet:
    """
    Return an object with all ACL definitions.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target ACL definition
        self.acl = self.api.acl.target_object()

    def launch(self):
        """
        Worker method used to construct the ACL endpoint definitions object.
        """
        
        # Construct the ACL object
        try:
            
            # If retrieving a single ACL definition
            if self.acl:
                
                # Get the ACL definition
                acl_definition = DBAuthACLKeys.objects.filter(uuid=self.acl).values()
                
                # If the ACL definition doesn't exist
                if not acl_definition:
                    return invalid('Could not locate ACL [%s] in the database' % self.acl)
                
                # Return the ACL definition
                return valid(json.dumps(acl_definition[0]))
            
            # If retrieving all ACL definitions
            else:
                return valid(json.dumps(list(DBAuthACLKeys.objects.all().values())))
            
        # Error during ACL construction
        except Exception as e:
            return invalid(self.api.log.exception('Failed to retrieve ACL definition(s): %s' % str(e)))

class AuthRequest:
    """
    Class used to handle token requests.
    """
    def __init__(self, parent):
        self.api = parent
        
    def launch(self):
        """
        Worker method used to process token requests and return a token if the API
        key is valid and authorized.
        """
        
        # Get the API token
        api_token = APIToken().get(id=self.api.request.user)
        
        # Handle token retrieval errors
        if api_token == False:
            return invalid(self.api.log.error('Error retreiving API token for user [%s]' % self.api.request.user))
        else:
            
            # Return the API token
            return valid({'token': api_token})