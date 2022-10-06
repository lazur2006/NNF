from lib._wrapper_scrapedatabase import wr_scrapeDatabase
from lib.basket import basket_manager

class create_cards(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.obj_scrapedatabase = wr_scrapeDatabase()
        self.basket_manager = basket_manager()
        pass

    def get_cards_data(self,cards_ids):
        retval=self.obj_scrapedatabase.get_byID(cards_ids)
        retval.update({"recipe_ingredients":
        [[(
            r[0],
            r[1]*self.basket_manager.get_num_scaled_by_base(),r[2],r[3]) if r[1] != '' else (r[0],r[1],r[2],r[3]
            ) 
            for r in e] 
            for e in retval['recipe_ingredients']]})
        return(retval)

    def get_basket(self,cards_ids):
        retval = {"cards_data":self.get_cards_data(cards_ids), "cards_overall_ingredients":self.basket_manager.build_basket(cards_ids)}
        retval['cards_data'].update({'recipe_ingredients':[[r+('ℹ️' if retval['cards_overall_ingredients']['unique_basket_elements']['amount'][retval['cards_overall_ingredients']['unique_basket_elements']['name'].index(r[3])]==r[1] else '',) for r in e] for e in retval['cards_data']['recipe_ingredients']]})
        return(retval)
        