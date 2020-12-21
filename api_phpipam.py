''' Requests is used to send HTTP GET and POST messages, allows for REST API access '''
import requests

''' Necessary for exit function '''
import sys

''' Stop SSL warnings '''
import urllib3
urllib3.disable_warnings()

def to_json(input):
    ''' Returns input in json format '''
    return json.dumps(input, indent = 2, sort_keys=True)

class phpipam:

    ''' This class is used to interact with the PHPIPAM API '''
    
    def __init__(self, **kwargs):

        '''We login to the IPAM to get a valid API token. Good way to make sure API is usable. 
           https://phpipam.net/api/api_documentation/ '''
        
        api_user      = "flaskcelery"
        self.section  = "15"
        self.base_url = f"http://100.70.4.224/api/{api_user}/"

        ''' User credentials '''
        username = "flaskcelery"
        password = "QLdOyeAzNg"

        ''' Test API by requesting a token '''
        self.token = self.get_token(username, password)
        # print ("Token: {}".format(self.token))
        return

    def get_token(self, username, password):

        ''' Retrieve API Token from PHPIPAM  '''

        url = "{}user/".format(self.base_url)
        r = requests.post(url, auth=(username, password), timeout=10, verify=False)
        if r.json()['code'] != 200:
            print("Error: Unable to get ipam token: " + str(r.json()))
            return
        return r.json()['data']['token']
    
    def send_get(self, **kwargs):

        ''' Get requests are used to retrieve information about objects from PHPIPAM'''

        ''' Send request, check for errors and print them out. '''
        try:
            response = requests.get(kwargs['url'], headers={'token': self.token }, timeout=10, verify=False)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("HTTP error: {}".format(e.response.text))
            return
        except requests.exceptions.ConnectionError as e:
            print("Connection error: {}".format(e.response.text))
            return
        except requests.exceptions.RequestError as e:
            print("Request error: {}".format(e.response.text))
            return
        
        ''' This assumes no errors were found so far. Let's process the json output, check for more errors and if none found return the data. '''
        response = response.json()
        if response['code'] != 200:
            print("Error: Unable to retrieve {}: {}".format(kwargs['url'], response))
        elif response['success'] == False:
            print("'{}' returned no data. Reason: {}".format(kwargs['url'], response['message']))
        elif 'data' in response:
            return response['data']

        return
    
    def send_post(self, **kwargs):

        ''' Post messages creating new entries in the IPAM with new values.
            Required input: payload - a dict containing the fields and their corresponding values '''

        ''' Send request, check for errors and print them out. '''
        try:
            response = requests.post(kwargs['url'], kwargs['payload'],  headers={'token': self.token }, timeout=10, verify=False)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("HTTP error: {}".format(e.response.text))
            return
        except requests.exceptions.ConnectionError as e:
            print("Connection error: {}".format(e.response.text))
            return
        except requests.exceptions.RequestException as e:
            print("Request error: {}".format(e.response.text))
            return
        
        ''' This assumes no errors were found so far. Let's process the json output, check for more errors and if none found return the data. '''
        response = response.json()
        if response['code'] != 201:
            print("Error: Unable to create object: {}".format(kwargs['url']))
            print("Payload: {}".format(kwargs['payload']))
            return

        return response

    def send_patch(self, **kwargs):

        ''' Patch messages update existin entries in the IPAM with new values.
            Required input: payload - a dict containing the fields and their corresponding values '''

        ''' Send request, check for errors and print them out. '''
        try:
            response = requests.patch(kwargs['url'], kwargs['payload'],  headers={'token': self.token }, timeout=10, verify=False)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("HTTP error: {}".format(e.response.text))
            return
        except requests.exceptions.ConnectionError as e:
            print("Connection error: {}".format(e.response.text))
            return
        except requests.exceptions.RequestException as e:
            print("Request error: {}".format(e.response.text))
            return
        
        ''' This assumes no errors were found so far. Let's process the json output, check for more errors and if none found return the data. '''
        response = response.json()
        if response['code'] != 200:
            print("Error: Unable to create object: {}".format(kwargs['url']))
            print("Payload: {}".format(kwargs['payload']))
            return

        return response

    ''' GET functions '''       
    def get_device_types(self, **kwargs):
        ''' Get all device types from IPAM. '''
        my_filter = ""
        if 'filter' in kwargs:
            key, value = kwargs['filter']
            my_filter = "?filter_by={}&filter_value={}".format(key, value)
        url = "{}tools/device_types/{}".format(self.base_url, my_filter)
        return self.send_get(url = url)

    def get_devices(self, **kwargs):
        ''' Get all devices from IPAM matching a specific device type.
            Available filters: id, hostname, ip_addr, description, sections, rack, location, type (device type id)
            Example filter: ipam.get_devices(filter = ['hostname', field.data]) '''
        my_filter = ""
        if 'filter' in kwargs:
            key, value = kwargs['filter']
            my_filter = "?filter_by={}&filter_value={}".format(key, value)
        url = "{}tools/devices/{}".format(self.base_url, my_filter)
        return self.send_get(url = url)

    def get_device_addresses(self, **kwargs):
        ''' Return all addresses attached to a device 
            Required input: device_id '''        
        url = "{}devices/{}/addresses/".format(self.base_url, kwargs['device_id'])
        return self.send_get(url = url)
        
    def get_device_subnets(self, **kwargs):
        ''' Return all subnets attached to a device 
            Required input: device_id  '''        
        url = "{}devices/{}/subnets/".format(self.base_url, kwargs['device_id'])
        return self.send_get(url = url)

    def get_section_subnets(self, **kwargs):
        ''' Get all subnets in a section '''

        section = self.section
        if 'section' in kwargs:
            section = kwargs['section_id']

        my_filter = ""
        if 'filter' in kwargs:
            key, value = kwargs['filter']
            my_filter = "?filter_by={}&filter_value={}".format(key, value)

        url = "{}sections/{}/subnets/{}".format(self.base_url, section, my_filter)
        return self.send_get(url = url)
        
    def get_vlans(self):        
        url = "{}vlan/".format(self.base_url)
        return self.send_get(url = url)
        
    def get_vrfs(self):
        url = "{}vrf/".format(self.base_url)
        return self.send_get(url = url)

    def get_vrf_subnets(self, **kwargs):
        ''' Required input: vrf_id '''
        url = f"{self.base_url}vrf/{kwargs['vrf_id']}/subnets/"
        return self.send_get(url = url)

    def get_address(self, **kwargs):
        ''' Required input: hostname '''
        if 'hostname' in kwargs:
            url = f"{self.base_url}addresses/search_hostname/{kwargs['hostname']}/"
            return self.send_get(url = url)
        return

    ''' POST functions '''
    def create_device(self, **kwargs):
        ''' Create a new device in IPAM. 
            Supported values to send along: hostname, ip_addr, description, type, sections, location (etc)
            Example payload dict: payload = { 'hostname': "DERP", 'description': "HERP" } '''
        payload = kwargs['payload']
        url = "{}devices/".format(self.base_url)
        return self.send_post(url = url, payload = payload)

    def create_address(self, **kwargs):
        ''' Create a new address in IPAM. 
            Required input:
             - subnet_id, if you want it to take the first available address
             - payload, always required. Supported values: id, subnetId, hostname, deviceId '''
        payload = kwargs['payload']

        ''' Different API calls depending on if you want to assign a specific IP or just take the first free one '''
        url = "{}addresses/".format(self.base_url)
        if not 'ip' in payload:
            subnet_id = kwargs['subnet_id']
            url = "{}addresses/first_free/{}/".format(self.base_url, subnet_id)
        return self.send_post(url = url, payload = payload)

    def create_subnet(self, **kwargs):
        ''' Create a new subnet in IPAM. 
            Required input:
            - supernet: which supernet to create the subnet under
            - mask: size of subnet
            Required payload:
            - sectionId: which section subnet belongs to
            Optional payload: 
            - device
            - vlanId
            - vrfId
            - subnet (IP) '''
        supernet = kwargs['supernet']
        mask     = kwargs['mask']

        payload  = kwargs['payload']
        if not 'section' in payload:
            payload['sectionId'] = self.section

        url = "{}subnets/{}/first_subnet/{}/".format(self.base_url, supernet, mask)
        return self.send_post(url = url, payload = payload)

    ''' PATCH functions '''
    def update_device(self, **kwargs):
        ''' Example:
            payload = {
                'id': device['id'],
                'hostname': new_name
            }
            ipam.update_device(payload = payload) '''
        payload = kwargs['payload']
        url = "{}devices/".format(self.base_url)
        return self.send_patch(url = url, payload = payload)
        
    def update_subnet(self, **kwargs):
        ''' Example:
            payload = {
                'id': subnet['id'],
                'description': new_name
            }
            ipam.update_subnet(payload = payload) '''
        payload = kwargs['payload']
        url = "{}subnets/".format(self.base_url)
        return self.send_patch(url = url, payload = payload)

    def update_address(self, **kwargs):
        ''' Example:
            payload = {
                'id': address['id'],
                'hostname': new_name
            }
            ipam.update_address(payload = payload) '''
        payload = kwargs['payload']
        address_id = payload.pop('id')
        url = "{}addresses/{}/".format(self.base_url, address_id)
        return self.send_patch(url = url, payload = payload)