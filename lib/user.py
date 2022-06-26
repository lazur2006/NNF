import keyring
import sqlite3
import hashlib
import secrets
import dotenv
import os
from os.path import exists

from cryptography.fernet import Fernet

class user(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''            
        try:
            open(".env","x").close()
            self.dotenv_file = dotenv.find_dotenv()
            dotenv.load_dotenv(self.dotenv_file)
            dotenv.set_key(self.dotenv_file, "salt", Fernet.generate_key().decode("UTF-8"))
        except:
            self.dotenv_file = dotenv.find_dotenv()
            dotenv.load_dotenv(self.dotenv_file)        
    
    def encrypt(self, message: bytes, key: bytes) -> bytes:
        return Fernet(key).encrypt(message)

    def decrypt(self, token: bytes, key: bytes) -> bytes:
        return Fernet(key).decrypt(token)
    
    def setCredentials(self,vendor,username,password,ipaddress):

        password = self.encrypt(password.encode(), bytes(dotenv.get_key(self.dotenv_file, "salt"),"UTF-8"))

        # try:
        #     keyring.delete_password(vendor, username)
        # except:
        #     pass  
        # keyring.set_password(vendor, username, password)
        
        ''' create SQlite db file '''
        conn = sqlite3.connect('static/db/user.db')

        try:
            conn.execute('''CREATE TABLE USER (VENDOR TEXT NOT NULL, USERNAME TEXT NOT NULL, PASSWORD TEXT NOT NULL, IPADDRESS TEXT NOT NULL, UNIQUE(VENDOR));''')
        except:
            ''' Already created '''
            pass

        ''' Try insert the values '''
        conn.execute("INSERT OR IGNORE INTO USER (VENDOR,USERNAME,PASSWORD,IPADDRESS) VALUES (?,?,?,?)",
                     (vendor,username,password,ipaddress)
                     )   
        ''' Otherwise the values may be updated '''
        conn.execute("UPDATE OR IGNORE USER SET USERNAME = ?, IPADDRESS = ?, PASSWORD = ? WHERE VENDOR = ?",
                     (username,ipaddress,password,vendor)
                     )    


        conn.commit()
        conn.close()
        
    def getUserData(self,vendor):
        try:
            conn = sqlite3.connect('static/db/user.db')
            userdata = conn.execute("SELECT USERNAME, IPADDRESS, PASSWORD FROM 'USER' WHERE VENDOR = ?",(vendor,)).fetchall()
            conn.close()
        except:
            userdata = ""
            
        return(userdata)
    
    def getPassword(self,vendor,username):
        #return(keyring.get_credential(vendor, username).password)
        return(self.decrypt(self.getUserData(vendor)[0][2], bytes(dotenv.get_key(self.dotenv_file, "salt"),"UTF-8")).decode())
    
    def getCredentials(self,vendor):
        try:
            username = self.getUserData(vendor)[0][0]
            ipaddress = self.getUserData(vendor)[0][1]
            password = self.getPassword(vendor, username)
        except:
            username = ""
            password = ""
            ipaddress = ""
        return(dict({'username':username, 'password':password, 'ipaddress':ipaddress}))