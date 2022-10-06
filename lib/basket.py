import sqlite3
import numpy as np

class static(object):
    num_recipe_portions = 2
    num_supplier_base = {"HelloFresh":2,"KptnCook":1}

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

    def get_num_recipe_portions(self):
        return(static.num_recipe_portions)

    def get_num_scaled_by_base(self):
        return(static.num_recipe_portions/static.num_supplier_base.get('HelloFresh'))

    def set_num_recipe_portions(self,num):
        static.num_recipe_portions = num

    def modify_recipe_portions(self,f):
        if f=='plus' and self.get_num_recipe_portions() < 10:
            self.set_num_recipe_portions(self.get_num_recipe_portions() + 1)
        elif f=='minus' and self.get_num_recipe_portions() > 1:
            self.set_num_recipe_portions(self.get_num_recipe_portions() - 1)
        elif f=='default':
            pass
        return(self.get_num_recipe_portions())

    def build_basket(self,basket_ids):
        conn = sqlite3.connect('static/db/recipe.db')

        #get the desired uid,names,img with basket_ids
        query = f"""SELECT ID, RECIPE_NAME, RECIPE_IMG FROM RECIPE WHERE ID in {e if len(e:=basket_ids) !=1 else "("+str(e[0])+")"} ORDER BY RECIPE_NAME;"""
        basket_recipes = list(map(list, zip(*conn.execute(query).fetchall())))

        query = f"""SELECT AMOUNT,UNIT,INGREDIENT,IMG FROM INGREDIENTS WHERE UID in {e if len(e:=basket_ids) !=1 else "("+str(e[0])+")"}"""
        basket_ingredients = list(map(list, zip(*conn.execute(query).fetchall())))
        unique_items, unique_item_ids, c = np.unique(basket_ingredients[2], return_inverse=True, return_counts=True)
        basket_ingredients[0] = [0.0 if e == '' else float(e) for e in basket_ingredients[0]]
        conn.close()

        t=[{
            'unit_specification':np.unique([basket_ingredients[1][idx_inner] for idx_inner,e_inner in enumerate(unique_item_ids) if e_inner == idx],return_inverse=True),
            'amounts':[basket_ingredients[0][idx_inner] for idx_inner,e_inner in enumerate(unique_item_ids) if e_inner == idx],
            'name':list(np.unique([basket_ingredients[2][idx_inner] for idx_inner,e_inner in enumerate(unique_item_ids) if e_inner == idx])),
            } for idx,e in enumerate(c)]

        u=[[
            sum([e.get('amounts')[ix]*self.get_num_scaled_by_base() for ix,n in enumerate(e.get('amounts')) if e.get('unit_specification')[1][ix]==idx]) 
            for idx,r in enumerate(e.get('unit_specification')[0])] 
            for e in t
            ]

        v = [[str(u[idx][ix]) + " " + str(r) for ix,r in enumerate(e.get('unit_specification')[0])] for idx,e in enumerate(t)]

        w = [' & '.join([r for r in e]) for e in v]

        return({"basket_recipe_elements":
            {
            "recipe_id":basket_recipes[0],
            "recipe_name":basket_recipes[1],
            "recipe_img":basket_recipes[2]
            },
            "unique_basket_elements":{
                "amount":[sum(np.array(basket_ingredients[0])[(unique_item_ids==idx[0])]*self.get_num_scaled_by_base()) for idx in enumerate(unique_items)],
                "unit":[np.array(basket_ingredients[1])[(unique_item_ids==idx[0])].tolist()[0] for idx in enumerate(unique_items)],
                "printable_unit_amounts":w,
                "name":[np.array(basket_ingredients[2])[(unique_item_ids==idx[0])].tolist()[0] for idx in enumerate(unique_items)],
                "image":[np.array(basket_ingredients[3])[(unique_item_ids==idx[0])].tolist()[0] for idx in enumerate(unique_items)]
                }
        }
        )
