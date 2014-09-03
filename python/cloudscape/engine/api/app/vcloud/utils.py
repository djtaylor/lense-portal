import re
import requests
import xml.etree.ElementTree as ET

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.app.vcloud.models import DBVCloudOrg, DBVCloudVDC

"""
Cache VCloud API Information
"""
class VCloudCache:
    def __init__(self, parent):
        self.api      = parent

        # VCloud API Token
        self.vc_token = None

        # Base API URL
        self.api_base = None

        # API request headers
        self.api_head = None

        # API mapper
        self.api_map  = None

    # Parse the XML response
    def vc_request(self, url):
        response = requests.get(url, headers=self.api_head, verify=False)
        xml_tree = ET.fromstring(responseZZ.text)
        return xml_tree

    # Cache VMs
    def _cache_vm(self, vm_elem):
        vm_name = vm_elem.attrib['name']
        vm_href = vm_elem.attrib['href']
        vm_uuid = re.compile('^.*vApp\/vm-(.*$)').sub(r'\g<1>', vm_href)
        self.api.log.info('Caching -> VM: %s, UUID: %s, API HREF: %s' % (vm_name, vm_uuid, vm_href))
        
        # JSON converted object
        vm_attr = {}
        
        # Element tags to query
        et = {
            'hw':    'VirtualHardwareSection', 
            'os':    'OperatingSystemSection', 
            'net':   'NetworkConnectionSection', 
            'guest': 'GuestCustomizationSection', 
            'run':   'RuntimeInfoSection'
        }
        
        # Subelement tags and objects
        se = {}
        
        # Fun times - start converting to JSON, why does the XML format suck so bad
        for vm_child in vm_elem:
            ns = re.compile('(^{[^}]*}).*$').sub(r'\g<1>', vm_child.tag)
            em = re.compile('^{[^}]*}(.*$)').sub(r'\g<1>', vm_child.tag)
            for et_tag, et_val in et.iteritems():
                if em == et_val:
                    se[et_tag] = '%s%s' % (ns,em)

        # Construct the subelements
        for se_tag, se_ns in se.iteritems():
            se_obj = ET.SubElement(vm_elem, se_ns)
            self.api.log.info(ET.tostringlist(se_obj))

    # Cache organizations
    def _cache_orgs(self, xml):
        
        # Drop the old tables
        #DBVCloudOrg.objects.all().delete()
        #DBVCloudVDC.objects.all().delete()
        #DBVCloudVApp.objects.all().delete()
        #DBVCloudVM.objects.all().delete()
        
        # Cache each organization and their resources
        for child in xml:
            
            # Extract the top level details
            org_name    = child.attrib['name']
            org_href    = child.attrib['href']
            org_uuid    = re.compile('^.*org\/(.*$)').sub(r'\g<1>', org_href)
            self.api.log.info('Caching -> Organization: %s, UUID: %s, API HREF: %s' % (org_name, org_uuid, org_href))
            
            # Get the child organization details
            org_href    = child.attrib['href']
            org_details = self.vc_request(org_href)
            for org_child in org_details:
                child_type = '' if not 'type' in org_child.attrib else org_child.attrib['type']
                
                # VCloud VDCs
                if 'vnd.vmware.vcloud.vdc' in child_type:
                    vdc_name = org_child.attrib['name']
                    vdc_rel  = org_child.attrib['rel']
                    vdc_href = org_child.attrib['href']
                    vdc_uuid = re.compile('^.*vdc\/(.*$)').sub(r'\g<1>', vdc_href)
                    self.api.log.info('Caching -> VDC: %s, UUID: %s, Rel: %s, API HREF: %s' % (vdc_name, vdc_uuid, vdc_rel, vdc_href))
                    
                    # Get the child VDC details
                    vdc_details = self.vc_request(vdc_href)
                    for vdc_child in vdc_details:
                        if 'ResourceEntities' in vdc_child.tag:
                            for vdc_res in vdc_child:
                                child_type = '' if not 'type' in vdc_res.attrib else vdc_res.attrib['type']
                                if 'vnd.vmware.vcloud.vApp' in child_type:
                                    vapp_name = vdc_res.attrib['name']
                                    vapp_href = vdc_res.attrib['href']
                                    vapp_uuid = re.compile('^.*vApp\/vapp-(.*$)').sub(r'\g<1>', vapp_href)
                                    self.api.log.info('Caching -> VApp: %s, UUID: %s, API HREF: %s' % (vapp_name, vapp_uuid, vapp_href))
                                    
                                    # Get VMs in VApp
                                    vapp_elems = self.vc_request(vapp_href)
                                    for vapp_elem in vapp_elems:
                                        if 'Children' in vapp_elem.tag:
                                            for vapp_child in vapp_elem:
                                                self._cache_vm(vapp_child)
            break

    # Construct the API mapper
    def _mapper(self):
        return {
            'orgs': {
                'url':     '%s/org/' % self.api_base,
                'handler': self._cache_orgs
            }
        }

    # Connect to the VCloud API server
    def _connect(self):
        
        # Make sure the VCloud connector is configured
        if not hasattr(self.api.conf, 'vcloud'):
            return invalid(self.api.log.error('Missing VCloud connector details in configuration'))
            
        # Make sure the required configuration values are set
        required = ['host', 'version', 'user', 'passwd']
        for key in required:
            if not hasattr(self.api.conf.vcloud, key):
                return invalid(self.api.log.error('Missing VCloud connector key \'%s\' in configuration' % key))
            
        # Set the base API url
        self.api_base = 'https://%s/api' % self.api.conf.vcloud.host
            
        # Define the authentication request headers and URL
        auth_headers  = {'Accept': 'application/*+xml;version%s' % self.api.conf.vcloud.version}
        auth_url      = '%s/sessions' % self.api_base
        self.api.log.info('Authenticating with VCloud Director API endpoint: %s' % auth_url)
            
        # Make an authentication request
        response      = requests.post(auth_url, auth=(self.api.conf.vcloud.user, self.api.conf.vcloud.passwd), headers=auth_headers, verify=False)
        
        # Make sure the response is OK
        if not response.status_code == 200:
            return invalid(self.api.log.error('Failed to authenticate with VCloud API: %s' % response.text))
        
        # Save the authentication token
        self.vc_token = response.headers['x-vcloud-authorization']
        
        # Set the new request headers
        self.api_head = {'Accept': 'application/*+xml;version%s' % self.api.conf.vcloud.version, 'x-vcloud-authorization': self.vc_token}
        
        # Connection is valid
        return valid()

    # Cache all the data in the VCloud API
    def launch(self):
        self.api.log.info('Running VCloud API data cache...')
        
        # Make the auhentication request and initial connection
        connect_rsp = self._connect()
        if not connect_rsp['valid']:
            return connect_rsp
        
        # Construct the API mapper
        self.api_map = self._mapper()
        
        # Get the response for each map element
        for api_group, api_obj in self.api_map.iteritems():
            api_obj['handler'](self.vc_request(api_obj['url']))
            
        # Return a valid response
        return valid('Test complete')