from python_picnic_api import PicnicAPI


class picnicapi(object):
    '''
    classdocs
    '''


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
            return(self.picnic.session.authenticated)
        except:
            return(False)
        
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
                   'price': val[0].get('price',0)/100 if val else 0, # init is 0€
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