import requests
import json
import urllib.parse
import uuid
import datetime

base_address = "https://api.getbring.com/rest"
x_bring_api_key = "cof4Nc6D8saplXjE3h3HXqHH8m7VU2i1Gs0g85Sp"
host = "api.getbring.com"
list_theme = "ch.publisheria.bring.theme.home"

class bring():

    def __init__(self):
        self.session = requests.session()

    def login(self,username,password):
        url = f"{base_address}/v2/bringauth"
        payload = f"email={urllib.parse.quote(username)}&password={password}"
        headers = {
        'host': host
        }
        try:
            response = self.session.request("POST", url, headers=headers, data=payload).json()
            if response.get('error'):
                response = False
            else:
                self.bearer_token = response.get('access_token')
                self.user_uuid = response.get('uuid')
                response = True
        except:
            response = False
        return(response)

    def add_item(self,list_uuid,item,specification):
        url = f"{base_address}/v2/bringlists/{list_uuid}/items"
        payload = json.dumps(
            {"changes":
            [
            {"operation":"TO_PURCHASE",
            "itemId": item,
            "spec":specification,
            "uuid":str(uuid.uuid4())}],
            "sender":"null"
            })
        headers = {
        'host': host,
        'authorization': f'Bearer {self.bearer_token}'
        }
        self.session.request("PUT", url, headers=headers, data=payload)

    def get_all_lists(self):
        url = f"{base_address}/bringusers/{self.user_uuid}/lists"
        payload={}
        headers = {
        'host': host,
        'x-bring-api-key': x_bring_api_key
        }
        return(self.session.request("GET", url, headers=headers, data=payload).json())

    def create_list(self,name):
        #get all lists created so far
        lists = self.get_all_lists()

        if not name in [e.get('name') for e in lists.get('lists')]:
            url = f"{base_address}/bringusers/{self.user_uuid}/lists"
            payload = f"name={urllib.parse.quote(name)}&theme={list_theme}"
            headers = {
            'host': host,
            'x-bring-api-key': x_bring_api_key
            }
            list_uuid = self.session.request("POST", url, headers=headers, data=payload).json().get('bringListUUID')
        else:
            list_uuid = [e.get('listUuid') for e in lists.get('lists') if e.get('name') == name][0]

        return(list_uuid)

    def search(self,vendorbasket):
        list_name = f"Nice'n Fresh 🍜  {datetime.date.today()}"
        list_uuid = self.create_list(list_name)
        [self.add_item(list_uuid,e,str(vendorbasket.get('amount')[idx]) + " " + str(vendorbasket.get('unit')[idx])) for idx,e in enumerate(vendorbasket.get('name'))]
        return("immediately_push_vendor_basket")

    def get_list_items(self,list_uuid):
        url = f"{base_address}/v2/bringlists/{list_uuid}"
        headers = {
        'host': host,
        'authorization': f'Bearer {self.bearer_token}'
        }
        return(self.session.request("GET", url, headers=headers).json())