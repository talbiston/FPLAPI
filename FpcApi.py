from typing import List, json
import requests
import json
import sys

class Fpc:

    def __init__(self, user, password, hostname):
        self.fpc_sid = ''
        self.user = user
        self.password = password
        self.url = f"https://{hostname}/fpc/api" 
        self.session = requests.session()

    def _main(self, action, uri, data=''):
        url = self.url
        try:
            if action == 'post':
                res = self.session.post(url + uri, headers=self.fpc_sid, json=data, verify=False)
                return res
            if action == 'get':
                res = self.session.get(url + uri, headers=self.fpc_sid, verify=False)
                return res
        except requests.exceptions.HTTPError:
            error = "An Http Error occurred: " + res.status_code
            sys.exit(error)
        except requests.exceptions.ConnectionError as errc:
            error = "An Error Connecting to the API occurred: " + str(errc)
            sys.exit(error)
        except requests.exceptions.Timeout as errt:
            error = "A Timeout Error occurred: " + str(errt)
            sys.exit(error)
        except requests.exceptions.RequestException as err:
            error = "An Unknown Error occurred: " + str(err)
            sys.exit(error)


    def login(self):
        data = {"user" : self.user, "password" : self.password}
        res = self._main('post', uri='/login', data=data)
        res_json = json.loads(res.text)
        self.fpc_sid = {'fpc-sid': res_json['fpc-sid']}
  
    def logout(self):
        res = self._main('post', uri='/logout')
        return res.status_code

    def getControllers(self):
        res = self._main('get', uri='/controllers')
        return res

    # Customer Calls

    def getCustomers(self):
        res = self._main('get', uri='/customers')
        return json.loads(res.text)

    def getCustomerById(self, cid):
        res = self._main('get', uri=f'/customers/{cid}')
        return json.loads(res.text)

    def getCustomerByName(self, customerName):
        customers = json.loads(self.getCustomers().text)
        for item in customers:
            if item.get('customerName') == customerName:
                data = self.getCustomerById(item.get('customerId'))
                return data

    def createCustomer(self, customerName, contactFname, contactLname, contactEmail, totalStorage, address1="", address2=""):
        data = {'customerName': customerName, 'contactFname': contactFname, 'contactLname': contactLname, 
        'contactEmail':contactEmail, 'totalStorage': totalStorage, 'address1': address1, 'address2': address2}
        res = self._main('post', uri="/customers", data=data)
        return res

    def _getCustomerRequired(self, cid):

        required = self.getCustomerById(cid)
        
        options = {}
        options['customerName'] = required['customerName']
        options['contactFname'] = required['contactFname']
        options['contactLname'] = required['contactLname']
        options['contactEmail'] = required['contactEmail']
        options['totalStorage'] = required['totalStorage']
        return options


    def updateCustomerById(self, cid, contactFname=None , contactLname=None, contactEmail=None, totalStorage=None, city=None, state=None, _zip=None, phone=None, 
    fax=None, collectorStoragePercentage=None):

        kwargs = {'contactFname': contactFname, 'contactLname': contactLname, 'contactEmail': contactEmail,
                 'totalStorage': totalStorage, 'city': city, 'state': state, 'zip': _zip, 'phone': phone,
                 'fax': fax, 'collectorStoragePercentage': collectorStoragePercentage}

        options = self._getCustomerRequired(cid)

        for k, v in kwargs.items():
            if v is not None:
                options[k] = v

        res = self._main('post', uri=f'/customers/{cid}', data=options)
        return res

    def updateCustomerByName(self, customerName, contactFname=None , contactLname=None, 
                            contactEmail=None, totalStorage=None, city=None, state=None, 
                            _zip=None, phone=None, fax=None, collectorStoragePercentage=None):
        customer = self.getCustomerByName(customerName)
        res = self.updateCustomerById(customer['customerId'], contactFname=contactFname, 
                                      contactLname=contactLname, contactEmail=contactEmail, totalStorage=totalStorage, 
                                      city=city, state=state, _zip=_zip, phone=phone, fax=fax, 
                                      collectorStoragePercentage=collectorStoragePercentage)
        return res

    def deleteCustomer(self, cid):
        '''
        Not working for some reason!
        '''
        res = self._main('post', uri=f'customers/{cid}/delete')
        return res.status_code

    # Customer Adoms

    def getCustomerAdoms(self, cid):
        res = self._main('get', uri=f'/customers/{cid}/adoms')
        return json.loads(res.text)

    def setCustomerAdoms(self, id, cid, adoms=[]):
        data = {'id': id, 'customerId': cid, 'adoms': adoms}
        res = self._main('post', uri=f'/customers/{cid}/adoms', data=data)
        return res.status_code

    # Customer users

    def getCustomerUsers(self, cid):
        res = self._main('get', uri=f'/customers/{cid}/users')
        return json.loads(res.text)


    def getCustomerUser(self, cid, uid):
        res = self._main('get', uri=f'/customers/{cid}/users/{uid}')
        return json.loads(res.text)

    def createCustomerUser(self, cid, userName, firstName, lastName, email, password):
        '''
        Getting a 500 code server error 
        '''
        data = {'userName': userName, 'firstName': firstName, 'lastName': lastName, 'email': email, 'password':password}
        res = self._main('post', uri=f'/customers/{cid}/users', data=data)
        return res.status_code

    # FortiManager 

    def getFortiMangers(self):
        res = self._main('get', uri='/fortimanagers')
        return json.loads(res.text)

    def getFortiManger(self, fmid):
        res = self._main('post', uri=f'/fortimanagers/{fmid}')
        return json.loads(res.text)

    def createFortimanager(self, fortiManagerName, ipAddress, adminUserName, adminPassword, frequencyValue, portNumber):
        data = {'fortiManagerName': fortiManagerName,'ipAddress': ipAddress,'adminUserName': adminUserName,
        'adminPassword': adminPassword,'frequencyValue': frequencyValue,'portNumber': portNumber}
        res = self._main('post', uri='/fortimanagers', data=data)
        return json.loads(res.text)

    def editFortimanager(self, fmid, fortiManagerName=None, ipAddress=None, adminUserName=None, adminPassword=None, frequencyValue=None, 
                        portNumber=None):
        data = {'fortiManagerName': fortiManagerName,'ipAddress': ipAddress,'adminUserName': adminUserName,
        'adminPassword': adminPassword,'frequencyValue': frequencyValue,'portNumber': portNumber}
        required = self.getFortiManger(fmid)
        for k, v in data.items():
            if v is None:
                data[k] = required[k]
        res = self._main('post', uri=f'/fortimanagers/{fmid}', data=data)
        return res.status_code

    def deleteFortiManager(self, fmid):
        res = self._main('post', uri=f'/fortimanagers/delete/{fmid}')
        return res.status_code