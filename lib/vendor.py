from lib.user import user
from lib.API__REWE import ReweMobileApi
from lib.API__Picnic import picnicapi
from lib.API__HelloFresh import hellofresh
from lib.API__Bring import bring
from lib._wrapper_scrapeweeklys import wr_scrapeWeeklys
import os

class vendor(object):
    '''
    classdocs
    '''
    global early_dic
    global vendorbasket

    def __init__(self):
        '''
        Constructor
        '''
        global early_dic
        early_dic = dict({'REWE':False,
                          'Picnic':False,
                          'HelloFresh':False})
        
        self.user = user()
        self.REWE = ReweMobileApi()
        self.Picnic = picnicapi()
        self.HelloFresh = hellofresh()
        self.bring = bring()
        
        early_dic = dict({'REWE':self.login('REWE'),
                          'Picnic':self.login('Picnic'),
                          'HelloFresh':self.login('HelloFresh'),
                          'Bring':self.login('Bring')})
        self.early = early_dic
        
    def login(self,vendor):
        
        global early_dic
        
        credentials = self.user.getCredentials(vendor)
        
        if vendor == 'REWE':
            auth = self.REWE.login(
                credentials['username'],
                credentials['password'],
                credentials['ipaddress'])
            early_dic['REWE'] = auth
        elif vendor == 'Picnic':
            auth = self.Picnic.login(
                credentials['username'],
                credentials['password'])
            early_dic['Picnic'] = auth
        elif vendor == 'HelloFresh':
            auth = self.HelloFresh.login(
                credentials['username'],
                credentials['password'])
            early_dic['HelloFresh'] = auth
        elif vendor == 'Bring':
            auth = self.bring.login(
                credentials['username'],
                credentials['password'])
            early_dic['Bring'] = auth
            
        self.early = early_dic
        
        return(auth)

    def logout(self):
        try:
            os.remove("_cookies")
            os.remove("_misc")
            os.remove("_token")
            os.remove("static/db/user.db")
        except:
            pass
    
    def getUserInfo(self,vendor):
        
        if vendor == 'REWE':
            try:
                info = dict({'Actual Zip Code': str(self.REWE.marketZipCode),'Selected Service Type': self.REWE.serviceType})
            except:
                info = dict({'Actual Zip Code': '','Selected Service Type': ''})
        elif vendor == 'Picnic':
            info = dict({'Status':'Welcome using Picnic'})
        elif vendor == 'HelloFresh':
            info = self.HelloFresh.hellofresh.stream.get('LOGIN').get('user_data')
        elif vendor == 'Bring':
            info = dict({'Status':'Welcome using Bring'})
        
        return(info)

    def handleWeeklys(self):
        return(wr_scrapeWeeklys(credentials = [self.user.getCredentials('HelloFresh')['username'],self.user.getCredentials('HelloFresh')['password']]))
    
    def handleCheckout(self,ingredients,vendor):
        global vendorbasket
        
        if vendor == 'REWE':
            vendorbasket = self.REWE.search(ingredients)
        elif vendor == 'Picnic':
            vendorbasket = self.Picnic.search(ingredients)
        elif vendor == 'Bring':
            vendorbasket = self.bring.search(ingredients)
        
        return(vendorbasket)

    def handleMissingIngredients(self):
        global vendorbasket
        
        return(self.bring.missing(vendorbasket.get('missing')))
    
    def modify_basket(self,idx,fnc):
        global vendorbasket
        
        if fnc == 'add':
            vendorbasket['vendorbasket'][idx].update({"amount": (vendorbasket['vendorbasket'][idx].get("amount") + 1) if vendorbasket['vendorbasket'][idx].get("amount") < 99 else 99})
        elif fnc == 'minus':
            vendorbasket['vendorbasket'][idx].update({"amount": (vendorbasket['vendorbasket'][idx].get("amount") - 1) if vendorbasket['vendorbasket'][idx].get("amount") > 0 else 0})
        elif fnc == 'next':
            vendorbasket['vendorbasket'][idx].update({"selected": (vendorbasket['vendorbasket'][idx].get("selected") + 1) if vendorbasket['vendorbasket'][idx].get("selected") < len(vendorbasket['vendorbasket'][idx].get("results"))-1 else len(vendorbasket['vendorbasket'][idx].get("results"))-1})
            vendorbasket['vendorbasket'][idx].update({"selected_id": vendorbasket['vendorbasket'][idx].get("results")[vendorbasket['vendorbasket'][idx].get("selected")].get("product_id")})
        elif fnc == 'prev':
            vendorbasket['vendorbasket'][idx].update({"selected": (vendorbasket['vendorbasket'][idx].get("selected") - 1) if vendorbasket['vendorbasket'][idx].get("selected") > 0 else 0})
            vendorbasket['vendorbasket'][idx].update({"selected_id": vendorbasket['vendorbasket'][idx].get("results")[vendorbasket['vendorbasket'][idx].get("selected")].get("product_id")})
        
        vendorbasket['vendorbasket'][idx].update({"price": round(vendorbasket['vendorbasket'][idx].get("amount")*vendorbasket['vendorbasket'][idx].get("results")[vendorbasket['vendorbasket'][idx].get("selected")].get("price"),2)})
        vendorbasket.update({"total":round(sum([val['price'] for val in vendorbasket['vendorbasket']]),2)})

        return(vendorbasket)
    
    def push_basket(self,vendor):
        global vendorbasket
        
        if vendor == 'REWE':
            self.REWE.push(vendorbasket=vendorbasket)
        elif vendor == 'Picnic':
            self.Picnic.push(vendorbasket=vendorbasket)

        return({"missing":vendorbasket['missing']})
    
    