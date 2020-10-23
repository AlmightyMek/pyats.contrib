import requests
import getpass

from .creator import TestbedCreator

class Eveng(TestbedCreator):
    """ Eveng class (TestbedCreator)
    Creator for the 'Eveng' source. Retrieves device data using a REST API and 
    converts the data to a structured testbed file or object.
    
    Will prompt user for user credentials for the logged in eveng user.

    Args:
  
    CLI Argument           |  Class Argument
    ------------------------------------------------
   
    pyATS Examples:
        
    Examples:
        # Create testbed from EVE-NG server source
        creator = Eveng(inventory_name="inventory.ini")
     
    """

    def _init_arguments(self):
        """ Specifies the arguments for the creator.

        Returns:
            dict: Arguments for the creator.

        """
        return {
            'required': ['eveng_url', 'eveng_user','eveng_password'],
            'optional': {
                'encode_password': False,
                'topology': False,
                'verify': False,
                'username': None,
                'password': None,
                'tag_telnet': None
            }
        }

    def _get_password(self):
        """Use getpass to get the password from the user
        """
        self.password = {}
        self.password["password"] = getpass.getpass(prompt="Enter the eveng_user's password: ")

        return self.password


    def _admin_login(self,eveng_url,eveng_user,eveng_password):
        """This function handles the login to the EVE-NG
            server
        """
        self.login_dict.update(self._eveng_user)
        self.login_dict.update(self._get_password())
        console_dict = {"html5": "-1"}  #This will let us login with the Native console
        self.login_dict.update(console_dict)
        login_url = "api/auth/login"

        try:                                #Here we are passing in the Server ip
            req = Request('POST',F"{eveng_url}{login_url}" , data = (json.dumps(self.login_dict)))
            #self.cookies.update(req.cookies.get_dict())

            prepped = self.session.prepare_request(req)
            respone = self.session.send(prepped, verify=False)
            respone.raise_for_status()
            #print(self.cookies)

        except requests.exceptions.HTTPError as e:
            raise SystemExit(e)
            sys.exit(1)

        return respone

    def _get_lab_nodes(self,username,eveng_url,lab_name):
        """Gets the labs nodes of the specified lab by 
        checking the shared labs folder first then the base folder

        Example output:
            [place example output]  
        
        Returns:
            dict: response from the eveng server
        """

        try:
            #https://[public-ip]/api/labs/Shared/OSPF-LSAs.unl
            #Check the shared folder , then check the other folder below
            req = Request('GET',f"https://{eveng_url}/api/labs/Shared/{lab_name}.unl/nodes")
            prepped = self.session.prepare_request(req)
            respone = self.session.send(prepped, verify=self._verify)
            respone.raise_for_status()

        except requests.exceptions.HTTPError as e:
            raise e
            
        else:
            try:
                req = self.session.get(f"https://{eveng_url}/api/labs/{lab_name}/.unl/nodes", 
                verify=self._verify)

            except requests.exceptions.HTTPError as e:
                raise SystemExit(e)
                sys.exit(1)

        return respone.json()

    def _create_device_inventory(self,node_inventory):
        """Create the device inventory needed for 
        pyATS from the eveng server's response
        """
        ###define device template dict
        try:
            final_dict = {'devices': {}}
        
        except as e:  
            print(e)
        #Here we loop through the list we get back and create a testbed device_type

        try:
            for entry in range(len(node_inventory)):
                hostname = node_inventory[entry]['name']
                ip_address = node_inventory[entry]['ip']
                port = node_inventory[entry]['port']
                dict_template = {f'{hostname}':
                    {"ip": f'{ip_address}',
                    "port": f'{port}',
                    "protocol": "telnet",
                    "username" : "",
                    "password" : "",
                    "os": "",
                    "type": ""}}

                if dict_template["port"] == 0: #make sure the telnet port is not 0 , if it is exit and try again 
                    raise ValueError(f"{dict_template[hostname]}'s connection port is 0, make sure the device is running on the EVE-NG server")
                else:
                    final_dict['devices'].update(dict_template)
            
            return final_dict

        except:
            return None

    def _generate(self):
        """ Transforms Eveng data into testbed format.
        
        Returns:
            dict: The intermediate dictionary format of the testbed data.

        """
        pass