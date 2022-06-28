# from lib.user import user
# from lib.API__REWE import ReweMobileApi
# from lib.API__Picnic import picnicapi
# from lib.API__HelloFresh import hellofresh
#from lib._wrapper_scrapedatabase import wr_scrapeDatabase
import sqlite3
import numpy as np

class basket_manager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        #self.obj_scrapedatabase = wr_scrapeDatabase()
        pass
    def modify(self,basket_ids):

        conn = sqlite3.connect('static/db/recipe.db')
        if len(basket_ids) != 1:
            query = (f"""SELECT RECIPE.ID, RECIPE.RECIPE_NAME, RECIPE.RECIPE_IMG, INGREDIENTS.IMG, INGREDIENTS.AMOUNT,INGREDIENTS.UNIT,INGREDIENTS.INGREDIENT as INGREDIENT
            FROM RECIPE
            JOIN INGREDIENTS ON RECIPE.ID = INGREDIENTS.UID
            WHERE INGREDIENTS.UID in {basket_ids} ORDER BY INGREDIENT;""")
        else:
            query = (f"""SELECT RECIPE.ID, RECIPE.RECIPE_NAME, RECIPE.RECIPE_IMG, INGREDIENTS.IMG, INGREDIENTS.AMOUNT,INGREDIENTS.UNIT,INGREDIENTS.INGREDIENT as INGREDIENT
            FROM RECIPE
            JOIN INGREDIENTS ON RECIPE.ID = INGREDIENTS.UID
            WHERE INGREDIENTS.UID in ({basket_ids[0]}) ORDER BY INGREDIENT;""")
        Ingredients =  conn.execute(query).fetchall()
        Ingredients = list(map(list, zip(*Ingredients)))#[2:5]
        Ingredients[0] = list(dict.fromkeys(Ingredients[0]))
        Ingredients[1] = list(dict.fromkeys(Ingredients[1]))
        Ingredients[2] = list(dict.fromkeys(Ingredients[2]))
        
        #Ingredients = [[],['2','3','4','5'],["Stk","St","Stk","Stk"],["APFEL","APFEL","BANANE","APFEL"]]
        
        Ingredients[4] = [0.0 if x=='None' else x for x in Ingredients[4]]
        Ingredients[4] = list(map(float, Ingredients[4]))
        Ingredients[6], unq_inv, _ = np.unique(Ingredients[6], return_inverse=True, return_counts=True)
        Ingredients[3] = [np.array(Ingredients[3])[(unq_inv==idx[0])].tolist()[0] for idx in enumerate(Ingredients[6])]
        Ingredients[4] = [sum(np.array(Ingredients[4])[(unq_inv==idx[0])]) for idx in enumerate(Ingredients[6])]
        Ingredients[5] = [np.array(Ingredients[5])[(unq_inv==idx[0])][0] for idx in enumerate(Ingredients[6])]
        
        Ingredients[4] = list(map(float, Ingredients[4]))
        Ingredients[6] = Ingredients[6].tolist()
        
        ret = {"ID":Ingredients[0],
               "Name":Ingredients[1],
               "img_uri":Ingredients[2],
               "ingredient_img":Ingredients[3],
               "Amount":Ingredients[4],
               "Unit":Ingredients[5],
               "Ingredient":Ingredients[6]
               }
        
        Ingredients = ret
        
        conn.close()
        
        return(Ingredients)

    def acc_ingredients(self,basket_ids):

        pass
