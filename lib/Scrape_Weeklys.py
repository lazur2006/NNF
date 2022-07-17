""" TODO

...

"""
import requests
import json
import ssl
import datetime
import urllib3
from urllib3 import util

host = "https://gw.hellofresh.com"

'''
setup cipher suite
'''
ciphers = (
'''ECDHE-ECDSA-AES128-GCM-SHA256:'''
'''ECDHE-RSA-AES128-GCM-SHA256:'''
'''ECDHE-ECDSA-AES256-GCM-SHA384:'''
'''ECDHE-RSA-AES256-GCM-SHA384:'''
'''ECDHE-ECDSA-CHACHA20-POLY1305:'''
'''ECDHE-RSA-CHACHA20-POLY1305:'''
'''DHE-RSA-AES128-GCM-SHA256:'''
'''DHE-RSA-AES256-GCM-SHA384'''
)


class TLSAdapter(requests.adapters.HTTPAdapter):

    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super(TLSAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):        
        ctx = util.ssl_.create_urllib3_context(ciphers=ciphers, 
                                          cert_reqs=ssl.CERT_REQUIRED, 
                                          options=self.ssl_options)
        self.poolmanager = urllib3.PoolManager(*pool_args,
                                       ssl_context=ctx,
                                       **pool_kwargs)



class scrapeWeeklys(object):

    def __init__(self):
        super(scrapeWeeklys, self).__init__()
        # Mount session due to cloudflare's TLS fingerprint protection
        self.session = requests.session()
        self.adapter = TLSAdapter(ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
        self.session.mount("https://", self.adapter)
        self.stream = dict()
        self.week_num = 0
        
    def login(self,credentials):
        url = f"{host}/login?country=DE&locale=de-DE&scope=public%2Ccustomer"
        payload = json.dumps({
          "locale": "de_DE",
          "country": "DE",
          "username": credentials[0],
          "password": credentials[1]
        })
        headers = {
          'user-agent': 'HelloFresh/22.8 (com.hellofresh.HelloFresh; build:4616773; iOS 14.6.0) Alamofire/5.4.4'
        }
        self.stream['LOGIN'] = self.session.request("POST", url, headers=headers, data=payload).json()
        return(True if self.stream['LOGIN'].get('access_token',False) else False)
        
    def account(self):
        url = "https://www.hellofresh.de/gw/api/customers/me/subscriptions?country=de&locale=de-DE"
        headers = {
          'authorization': f"Bearer {self.stream['LOGIN']['access_token']}"
        }
        self.stream['ACCOUNT'] = self.session.request("GET", url, headers=headers).json()
        
    def weeklys(self):
        try:
            subscription = self.stream['ACCOUNT']['items'][0]['id']
        except:
            subscription = ""
            
        servings = "2" 
        try:
            product_sku = self.stream['ACCOUNT']['items'][0]['product']['sku']
        except:
            product_sku = ""
        preference = "light"
        try:
            postcode = self.stream['ACCOUNT']['items'][0]['shippingAddress']['postcode']
        except:
            postcode = ""
        delivery_option = ""

        my_date = datetime.date.today()
        year, self.week_num, _ = my_date.isocalendar()
        next_week = self.week_num + 1
        url = f"{host}/my-deliveries/menu?delivery-option={delivery_option}&postcode={postcode}&preference={preference}&product-sku={product_sku}&servings={servings}&subscription={subscription}&week={str(year)}-W{str(next_week)}&locale=de-DE&country=DE"
        headers = {
          'authorization': f"Bearer {self.stream['LOGIN']['access_token']}"
        }
        self.stream['WEEKLYS'] = self.session.request("GET", url, headers=headers).json()
