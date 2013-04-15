from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User

class EmailSender(object):
    sender = None
    sender_addr = 'reports@whitebaygroup.com'
  
    def __init__(self):
        print "email sender"
    
    def get_sender(self):
        return User.objects.get(username='EmailHost')
  
    def send_email(self, subject, content, addr_to, attach_path): 
        try:
            #self.sender = self.get_sender()
            #if self.sender != None:
            # auth_user=self.sender.email, auth_password=self.sender.first_name + self.sender.last_name
            message = EmailMessage(subject=subject, body=content, 
                                   from_email=self.sender_addr, to=[addr_to]) # addr_to should be a list
            message.attach_file(attach_path)
            message.send()
            return True
            #else:
                #return False
        except:
            return False
                        
                
