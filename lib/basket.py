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


    def build_basket(self,basket_ids):
        conn = sqlite3.connect('static/db/recipe.db')

        #get the desired uid,names,img with basket_ids
        query = f"""SELECT ID, RECIPE_NAME, RECIPE_IMG FROM RECIPE WHERE ID in {e if len(e:=basket_ids) !=1 else "("+str(e[0])+")"} ORDER BY RECIPE_NAME;"""
        basket_recipes = list(map(list, zip(*conn.execute(query).fetchall())))

        query = f"""SELECT AMOUNT,UNIT,INGREDIENT,IMG FROM INGREDIENTS WHERE UID in {e if len(e:=basket_ids) !=1 else "("+str(e[0])+")"}"""
        basket_ingredients = list(map(list, zip(*conn.execute(query).fetchall())))
        unique_items, unique_item_ids, _ = np.unique(basket_ingredients[2], return_inverse=True, return_counts=True)
        basket_ingredients[0] = [0.0 if e == '' else float(e) for e in basket_ingredients[0]]
        conn.close()

        return({"basket_recipe_elements":
            {
            "recipe_id":basket_recipes[0],
            "recipe_name":basket_recipes[1],
            "recipe_img":basket_recipes[2]
            },
            "unique_basket_elements":{
                "amount":[sum(np.array(basket_ingredients[0])[(unique_item_ids==idx[0])]) for idx in enumerate(unique_items)],
                "unit":[np.array(basket_ingredients[1])[(unique_item_ids==idx[0])].tolist()[0] for idx in enumerate(unique_items)],
                "name":[np.array(basket_ingredients[2])[(unique_item_ids==idx[0])].tolist()[0] for idx in enumerate(unique_items)],
                "image":[np.array(basket_ingredients[3])[(unique_item_ids==idx[0])].tolist()[0] for idx in enumerate(unique_items)]
                }
        }
        )