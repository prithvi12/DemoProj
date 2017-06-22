import ConfigParser, email, imaplib, io, requests
class ExtractEmailData(object):
   def setEmailCredentials(self):
       self.config = ConfigParser.ConfigParser()
       self.found = self.config.read('configuration.ini')
       if not self.found:
            raise ValueError('No config file found!')         
       else:
           self.smtp_server_url = self.config.get('Gmail', 'smtp_server_url')
           self.password = self.config.get('Gmail', 'password')
           self.email_id = self.config.get('Gmail', 'email_id')
           self.username = self.config.get('iContact', 'username')
           self.icontactpassword = self.config.get('iContact', 'password')
           self.app_id = self.config.get('iContact', 'app_id')
           self.folder_id = self.config.get('iContact', 'folder_id')

   def getEmailList(self):
         ExtractEmailData.setEmailCredentials(self)
         mail = ExtractEmailData.setMail(self)
         result, data = mail.uid('search', None, "ALL")     
         i = len(data[0].split()) 
         fromList = []
         for x in range(i):
            latest_email_uid = data[0].split()[x]
            result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')        
            raw_email = email_data[0][1]
            msg = email.message_from_string(raw_email)            
            #ExtractEmailData.getdatafromicontact(self,msg._payload[0]._payload)
            fromList.append(msg['From'].split())
         mail.logout()
         return fromList
   
   def setMail(self):
        mail = imaplib.IMAP4_SSL(self.smtp_server_url)
        mail.login(self.email_id,self.password)
        mail.list()
        mail.select("Marketing")
        return mail

