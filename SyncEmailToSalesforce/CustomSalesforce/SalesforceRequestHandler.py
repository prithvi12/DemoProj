import ConfigParser, requests, json, re, ast
class SalesforceRequestHandler:
    def connectToSalesforce(self):
        print "connecting to salesforce please wait..."
        SalesforceRequestHandler.setrequest(self)
        self.result = SalesforceRequestHandler.getaccesstoken(self)
        if self.result.reason == 'OK':
                body = json.loads(self.result.content)
                self.access_token = body["access_token"]
                self.instance_url = body["instance_url"]
        else :
                print self.result.reason
    def setrequest(self):
        self.config = ConfigParser.ConfigParser()
        self.found = self.config.read('configuration.ini')
        if not self.found:
            raise ValueError('No config file found!')
        self.client_id = self.config.get('Salesforce', 'client_id')
        self.password = self.config.get('Salesforce', 'password')
        self.client_secret = self.config.get('Salesforce', 'client_secret')
        self.username = self.config.get('Salesforce', 'username')
        self.sfurl = self.config.get('Salesforce', 'sfurl')
    def getaccesstoken(self):
        header =  {
                      'grant_type': 'password',
                      'client_id': self.client_id,
                      'client_secret': self.client_secret,
                      'username': self.username,
                      'password': self.password,
                      'Content-Type' : 'application/x-www-form-urlencoded'
                  }
        print self.sfurl
        result = requests.post( self.sfurl, headers={"Content-Type":"application/x-www-form-urlencoded"}, data=header )
        return result
    def setrequestheader(self):
        return   {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + self.access_token
                 }
    def query(self,strQuery):
            print "processing query please wait..."
            strQuery = re.sub(' +',' ',strQuery)            
            strQuery = re.sub(' ','+',strQuery)
            mapSalesforceData = {}
            print self.instance_url
            url = self.instance_url+'/services/data/v39.0/query/?q='+strQuery
            header = SalesforceRequestHandler.setrequestheader(self)
            response = requests.get(url,headers=header)
            if response.reason == 'OK':
                body = json.loads(response.text)
                if body['records']:
                    for record in body['records']:
                        mapSalesforceData[ast.literal_eval(json.dumps(record['Id']))] = json.dumps(record)                                                 
                        #del mapSalesforceData[json.dumps(record['Id'])]['attributes']
                    return mapSalesforceData
                else :
                    print "No previous records found with these email in salesforce database....."
                    return mapSalesforceData
            else :
                return response.reason
    def update(self,data):
        print "updating records..."
        url = self.instance_url+'/services/data/v39.0/composite/batch'
        lstToUpdate = []
        for record in data:
            lstToUpdate.append({ "method":"PATCH","url":"v39.0/sobjects/Contact/"+record['Id'],"richInput":record})
        for key in lstToUpdate:            
            del key['richInput']['Id']        
        mapNew = {}  
        mapNew['batchRequests'] = lstToUpdate
        header = SalesforceRequestHandler.setrequestheader(self)
        print json.dumps(mapNew)
        response = requests.post(url,json.dumps(mapNew),headers=header)
        print response