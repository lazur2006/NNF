from lib.user import user
from lib.API__REWE import ReweMobileApi
from lib.API__Picnic import picnicapi
from lib.API__HelloFresh import hellofresh

class vendor(object):
    '''
    classdocs
    '''
    global early_dic


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
        #print("REWE early login successful :: " + str(self.REWE.earlylogin))
        
        early_dic = dict({'REWE':self.login('REWE'),
                          'Picnic':self.login('Picnic'),
                          'HelloFresh':self.login('HelloFresh')})
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
            #search_results = self.REWE.searchItem("cola")
            #searchresultID = search_results[0]['_embedded']['articles'][0]['_embedded']['listing']['id']
            #self.REWE.addItem2Basket(searchresultID,2)
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
            
        self.early = early_dic
        
        return(auth)
    
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
        
        return(info)
    
    def handleCheckout(self,ingredients,vendor):
        
        if vendor == 'REWE':
            vendorbasket = ''
            pass
        elif vendor == 'Picnic':
            vendorbasket = self.Picnic.search(ingredients)
            pass
        elif vendor == 'PDF':
            vendorbasket = ''
            pass
        
        return(vendorbasket)
    
    