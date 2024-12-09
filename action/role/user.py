class User:
    def __init__(self, userid, username, email, pwd, role):
        self.userid = userid
        self.username = username
        self.pwd = pwd
        self.email = email 
        self.role = role   # role = 1 for admin, role = 2 for gambler
        
    def get_userid(self):
        return self.userid
      
    def get_username(self):
        return self.username
    
    def get_userpwd(self):
        return self.pwd
    
    def get_useremail(self):
        return self.email
      
    def get_role(self):
        return self.role

      
    
    