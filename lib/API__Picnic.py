from python_picnic_api import PicnicAPI
from hashlib import md5
import json, requests

# Monkey patching Picnic api search function
search = PicnicAPI.search
def inherited_search(self, *args, **kwargs):
    response = self.session.get(
            url="https://storefront-prod.de.picnicinternational.com/api/15/pages/search-page-results",
            params={
                "search_term": args[0],
            },
            headers={
                "x-picnic-agent": "20100;1.15.255-19252",
                "x-picnic-auth": "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4MDItMDgwLTA5ODIiLCJwYzpjbGlkIjoyMDEwMCwicGM6cHY6ZW5hYmxlZCI6dHJ1ZSwicGM6bG9naW50cyI6MTcxMTIxMzMyOTUxNSwicGM6ZGlkIjoiNkM5REQ2RUQtOEFBRC00M0U3LTlFMzQtNDM3QjYzNjNEMkVFIiwiaXNzIjoicGljbmljLWRldiIsInBjOnB2OnZlcmlmaWVkIjp0cnVlLCJwYzoyZmEiOiJWRVJJRklFRCIsImV4cCI6MTcyNjc2NTM3OSwiaWF0IjoxNzExMjEzMzc5LCJwYzpyb2xlIjoiU1RBTkRBUkRfVVNFUiIsImp0aSI6IkNXVkMyTkhaIn0.U2yA16Z2QdpM2LcyiTOQg-WloNbnLuy8TcLl3HGPLxN2suz1rOf4lPAjELcI8pyOPjuKRPsHscihTDyAgmJ5ltIPi1JtYqLIPq6PDURhT2ZwBknALKY4eoSds8pCS-h2OwyN3ksxXNHhAVz_PQ2P4hPJHTQTGtTKOFbeqd8kjoEi90Rkp4M0E7SRCLIBQFL_Phd1Zk9latqL4ejC6Ed--lJcmzTIeUwt7j-VOaFC39rMC6L_A7MGK5eS6n4pw9JYZ_C5gK502bnwMeutaQdAI9CUUUwRffhup3ueNbrKw93FDxI_wevEWu8mxYXWViqtlULQNKO9xZ6R_uuDLFfQCA",
            },
        )
    content=response.json()
    try:
        return [{'items':[e.get('content').get('selling_unit') for e in content.get('body').get('children')[0].get('children')[:-1]]}]
    except Exception as e:
        return [{}]
PicnicAPI.search = inherited_search

# Monkey::Picnic.login
login = PicnicAPI.login
def inherited_login(self, *args, **kwargs):
    url = "https://gateway-prod.global.picnicinternational.com/api/15/user/login"
    payload = json.dumps({"client_id": "20100","client_version": "1.15.255","device_id": "6C9DD6ED-8AAD-43E7-9E34-437B6363D2EE","device_name": "notAvailable","key": args[0],"secret": md5(args[1].encode("utf-8")).hexdigest()})
    headers = {'Host': 'gateway-prod.global.picnicinternational.com','picnic-email': args[0],'Content-Type': 'application/json'}
    e = None
    try:
        response = self.session.request("POST", url, headers=headers, data=payload)
        x_picnic_auth = response.headers._store.get('x-picnic-auth')[1]
    except Exception as e:
        print('issue when picnic login: ' + e)
    try:
        url = "https://storefront-prod.de.picnicinternational.com/api/15/user/2fa/generate"
        payload = json.dumps({"channel": "SMS"})
        headers = {'Host': 'storefront-prod.de.picnicinternational.com','x-picnic-agent': '20100;1.15.255-19252','x-picnic-auth': x_picnic_auth,'Content-Type': 'application/json'}
        response = self.session.request("POST", url, headers=headers, data=payload)
    except Exception as e:
        print('issue when SMS auth: ' + e)
    self.session._update_auth_token(x_picnic_auth)
PicnicAPI.login = inherited_login

class picnicapi(object):
    def __init__(self):
        '''
        Constructor
        '''
    def login(self,username,password):
        try:
            self.picnic = PicnicAPI(
                username=username,
                password=password,
                country_code='DE')
            return 'OTP_required'
            return(self.picnic.session.authenticated)
        except Exception as e:
            return(False)
        
    def otp(self,code):
        url = "https://storefront-prod.de.picnicinternational.com/api/15/user/2fa/verify"
        payload = json.dumps({"otp": str(code)})
        headers = {'Host': 'storefront-prod.de.picnicinternational.com','x-picnic-agent': '20100;1.15.255-19252','x-picnic-auth': self.picnic.session.auth_token,'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        self.picnic.session._update_auth_token(response.headers._store.get('x-picnic-auth')[1])
        return response.status_code
        
    def search(self,ingredients):
        
        results = [self.picnic.search(element)[0].get('items',[{}]) for element in ingredients['name']]   
        retval = {'total':0,
                  'missing':[],
                  'vendorbasket':[{'search_term':ingredients['name'][idx],
                   'search_amount':str(ingredients['printable_unit_amounts'][idx]),
                   'search_image_uri':ingredients['image'][idx],
                   'amount': 1, # just for initializing the default amount
                   'selected': 0, # just for initializing the default selected item
                   'selected_id': val[0].get('id') if val else 'no_id', # just for initializing the default selected item
                   'price': val[0].get('display_price',0)/100 if val else 0, # init is 0€
                   'results':[{
                    'product_id':arg.get('id'),
                    'name':arg.get('name','noname'),
                    'unit_quantity':arg.get('unit_quantity','noquant'),
                    'price':arg.get('price',arg.get('display_price',0))/100,
                    'image_uri':self.getImageUri(arg.get('image_id'))} for arg in val[:-1]]} for idx,val in enumerate(results)]}
        
        retval.update({"total":round(sum([val['price'] for val in retval['vendorbasket']]),2)})
        
        retval.update({"missing":[{"search_term":val['search_term'],"search_amount":val['search_amount'],"search_image_uri":val['search_image_uri']} for val in retval['vendorbasket'] if not val['results']]})
        
        return(retval)
        
    def getImageUri(self,image):
        return(f"https://storefront-prod.de.picnicinternational.com/static/images/{str(image)}/small.png")
    
    def push(self,vendorbasket):
        _ = [self.picnic.add_product(product_id=arg['selected_id'], count=arg['amount']) if arg['selected_id'] != 'no_id' else 'None' for arg in vendorbasket['vendorbasket']]