import ConfigParser, email, imaplib, io, requests, json
import CustomSalesforce.SalesforceRequestHandler as sForce
import ENZ_Email.ExtractEmailData as enziEmail
import ENZ_Salesforce.SyncEmailDataToSalesforce as enziSforce
import salesforce as sf
obj = enziEmail.ExtractEmailData()
fromList = []
fromList = obj.getEmailList()
print fromList
obj = sForce.SalesforceRequestHandler()
obj.connectToSalesforce()
obj1 = enziSforce.SyncEmailDataToSalesforce()
result = {}
result = obj1.upsert(fromList)
print result