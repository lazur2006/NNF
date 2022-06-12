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
        
        results = [self.picnic.search(element)[0].get('items',[{}]) for element in ingredients['Ingredient']]   
        retval = [{'search_term':ingredients['Ingredient'][idx],
                   'search_amount':str(ingredients['Amount'][idx]) + str(ingredients['Unit'][idx]),
                   'results':[{
                    'product_id':arg.get('id'),
                    'name':arg.get('name','noname'),
                    'unit_quantity':arg.get('unit_quantity','noquant'),
                    'price':arg.get('price',0)/100,
                    'image_uri':self.getImageUri(arg.get('image_id'))} for arg in val[:-1]]} for idx,val in enumerate(results)]
        
        return(retval)
        
    def getImageUri(self,image):
        return(f"https://storefront-prod.de.picnicinternational.com/static/images/{str(image)}/small.png")
        