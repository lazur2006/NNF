import keyring
import sqlite3

import keyring_jeepney


class user(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        #print("user")
        keyring.set_keyring(keyring_jeepney.Keyring())
        print("STOP")
    
    def setCredentials(self,vendor,username,password,ipaddress):
        try:
            keyring.delete_password(vendor, username)
        except:
            pass  
        keyring.set_password(vendor, username, password)
        
        ''' create SQlite db file '''
        conn = sqlite3.connect('static/db/user.db')

        try:
            conn.execute('''CREATE TABLE USER (VENDOR TEXT NOT NULL, USERNAME TEXT NOT NULL, IPADDRESS TEXT NOT NULL, UNIQUE(VENDOR));''')
        except:
            ''' Already created '''
            pass
        

        ''' Try insert the values '''
        conn.execute("INSERT OR IGNORE INTO USER (VENDOR,USERNAME,IPADDRESS) VALUES (?,?,?)",
                     (vendor,username,ipaddress)
                     )   
        ''' Otherwise the values may be updated '''
        conn.execute("UPDATE OR IGNORE USER SET USERNAME = ?, IPADDRESS = ? WHERE VENDOR = ?",
                     (username,ipaddress,vendor)
                     )    


        conn.commit()
        conn.close()
        
    def getUserData(self,vendor):
        try:
            conn = sqlite3.connect('static/db/user.db')
            userdata = conn.execute("SELECT USERNAME, IPADDRESS FROM 'USER' WHERE VENDOR = ?",(vendor,)).fetchall()
            conn.close()
        except:
            userdata = ""
            
        return(userdata)
    
    def getPassword(self,vendor,username):
        return(keyring.get_credential(vendor, username).password)
    
    def getCredentials(self,vendor):
        try:
            username = self.getUserData(vendor)[0][0]
            ipaddress = self.getUserData(vendor)[0][1]
            password = self.getPassword(vendor, username)
        except:
            username = ""
            password = ""
        return(dict({'username':username, 'password':password, 'ipaddress':ipaddress}))
    
    