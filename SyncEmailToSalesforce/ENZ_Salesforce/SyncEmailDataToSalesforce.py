import ConfigParser, email, imaplib, io, json,ast
import CustomSalesforce.SalesforceRequestHandler as sForce
import salesforce as sf
class SyncEmailDataToSalesforce(object):    
    def upsert(self,fromList):
        obj = sForce.SalesforceRequestHandler()
        obj.connectToSalesforce()
        arrayFields = ["FirstName", "LastName","Email","Marketing_Email_Count__c","Id"]
        array = []
        mapContacts = {}
        mapSalesforceRecordsToUpdate = {}
        setEmails = set()
        for apiNames in fromList:
            contact = {}
            index = 0;
            email = ''
            for contactField in apiNames:                
                if arrayFields[index] == 'Email':
                    email = contactField[contactField.find("<")+1:contactField.find(">")]
                    if mapContacts:                       
                        if email in mapContacts:
                              contact = mapContacts.get(email)
                              contact["Marketing_Email_Count__c"] = contact["Marketing_Email_Count__c"] + 1
                        else:
                              contact["Marketing_Email_Count__c"] = 1
                    else :
                        contact["Marketing_Email_Count__c"] = 1
                    contact[arrayFields[index]] = email                    
                    setEmails.add('\''+email+'\'')
                else:
                    contact[arrayFields[index]] = contactField
                index = index + 1
                array.append(contact)
            mapContacts[email] = contact
        mapContactWithIdToUpdate = {}
        mapContactWithIdToInsert = {}
        mapSalesforceContacts = {}
        try:
            mapSalesforceContacts = obj.query("SELECT Id, FirstName, LastName, Marketing_Email_Count__c, Email FROM Contact WHERE Email In ("+",".join(setEmails)+")")
            
            if mapSalesforceContacts.keys():                
                for recordId in mapSalesforceContacts.keys():
                    #ast.literal_eval(json.loads(mapSalesforceContacts[recordId])['Email'])          
                    mapSalesforceRecordsToUpdate[json.loads(mapSalesforceContacts[recordId])['Email']] = { "FirstName":json.loads(mapSalesforceContacts[recordId])['FirstName'],"LastName":json.loads(mapSalesforceContacts[recordId])['LastName'],"Id":recordId,"Marketing_Email_Count__c":json.loads(mapSalesforceContacts[recordId])['Marketing_Email_Count__c']}
            for key in mapContacts.keys():
                    if key in mapSalesforceRecordsToUpdate:
                        mapContactWithIdToUpdate[key] = mapSalesforceRecordsToUpdate[key]
                        mapContactWithIdToUpdate[key]['Marketing_Email_Count__c'] = mapContacts[key]['Marketing_Email_Count__c'] + mapContactWithIdToUpdate[key]['Marketing_Email_Count__c']
                    else :
                        mapContactWithIdToInsert[key] = mapContacts.get(key)
        except Exception, ex:
            print ex
        result = []
        resultAfterInsert = []
        resultAfterUpdate = []
        if mapContactWithIdToInsert.keys():
            sfdc = sf.Salesforce()
            config = ConfigParser.ConfigParser()
            config.read('configuration.ini')
            sfdc.authenticate(client_id=config.get('Salesforce', 'client_id'),client_secret=config.get('Salesforce', 'client_secret'),username=config.get('Salesforce', 'username'),password=config.get('Salesforce', 'password'))
            for key in mapContactWithIdToInsert.keys():
                obj = sfdc.contact.create(mapContactWithIdToInsert[key])
                resultAfterInsert.append(obj)
        if mapContactWithIdToUpdate.keys():
            for key in mapContactWithIdToUpdate.keys():
                mapContactWithIdToUpdate[key]['Email'] = key
            obj.update(mapContactWithIdToUpdate.values())
            result.append(mapContactWithIdToUpdate)
        if resultAfterInsert:
            result.append(resultAfterInsert)
        return result