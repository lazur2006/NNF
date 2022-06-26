# from lib.user import user
# from lib.API__REWE import ReweMobileApi
# from lib.API__Picnic import picnicapi
# from lib.API__HelloFresh import hellofresh
from lib._wrapper_scrapedatabase import wr_scrapeDatabase

class create_cards(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.obj_scrapedatabase = wr_scrapeDatabase()
        pass

    def get(self,basket):
        return(self.obj_scrapedatabase.get_byID(basket))