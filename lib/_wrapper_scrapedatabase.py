'''
Created on 21.05.2022

@author: n00b
'''
import sqlite3

class wr_scrapeDatabase(object):
    '''
    
    == Wrapper class for connecting the individual layers with each other ==
    == Connection between App (Flask) // ScrapeWeeklys ==
    
    '''


    def __init__(self):
        ''' scrape from database '''
    
    def safe_list_get(self,l, idx, default):
        try:
            return l[idx]
        except IndexError:
            return default
    
    def __get(self,cmd):
        conn = sqlite3.connect('static/db/recipe.db')
        
        try:
            retval = list(map(list, zip(*conn.execute(cmd).fetchall())))
            recipes = {
                "recipe_amount":len(retval[0]),
                "recipe_id":retval[0],
                "recipe_uid":retval[6],
                "recipe_title":retval[1],
                "recipe_link":retval[2],
                "recipe_subtitle":retval[3],
                "recipe_tag":retval[4],
                #"recipe_img":["static/images/de-DE/" + str(s) + ".jpg" for s in retval[0]] # OFFLINE VERSION
                "recipe_img":retval[5], #  ONLINE VERSION
                "recipe_type":[self.safe_list_get(conn.execute('''SELECT TAG FROM 'TAGS' WHERE UID=?;''',(id,)).fetchall(),0,[''])[0] for id in retval[0]],
                "recipe_instructions":[list(map(list, zip(*conn.execute('''SELECT INSTRUCTION FROM 'INSTRUCTIONS' WHERE UID=?;''',(id,)).fetchall())))[0] for id in retval[0]],
                "recipe_instructions_img":[list(map(list, zip(*conn.execute('''SELECT IMG FROM 'INSTRUCTIONS' WHERE UID=?;''',(id,)).fetchall())))[0] for id in retval[0]],
                "recipe_ingredients":[conn.execute('''SELECT INGREDIENTS.IMG,INGREDIENTS.AMOUNT,INGREDIENTS.UNIT,INGREDIENTS.INGREDIENT as INGREDIENT FROM RECIPE JOIN INGREDIENTS ON RECIPE.ID = INGREDIENTS.UID WHERE INGREDIENTS.UID in (?) ORDER BY INGREDIENT;''',(id,)).fetchall() for id in retval[0]]
                }
        except:
            recipes = {
                "recipe_amount":0,
                "recipe_id":"",
                "recipe_uid":"",
                "recipe_title":"",
                "recipe_link":"",
                "recipe_subtitle":"",
                "recipe_tag":"",
                "recipe_img":"",
                "recipe_type":"",
                "recipe_instructions":"",
                "recipe_instructions_img":"",
                "recipe_ingredients":""
                }
        
        
            
        conn.close()
        return(recipes)
     
    def get_random(self,limit):
        return(self.__get(f"SELECT * FROM 'RECIPE' ORDER BY RANDOM() LIMIT {limit};"))
    
    def get_byID(self,ID):
        if len(ID) != 1:
            return(self.__get(f"SELECT * FROM 'RECIPE' WHERE ID IN {tuple(ID)} ORDER BY ID;"))
        else:
            return(self.__get(f"SELECT * FROM 'RECIPE' WHERE ID IN ({ID[0]}) ORDER BY ID;"))
    
    def get_allNames(self):
        conn = sqlite3.connect('static/db/recipe.db')
        try:
            ret = conn.execute("SELECT RECIPE_NAME FROM 'RECIPE'").fetchall()
            ret = list(list(zip(*ret))[0])
        except:
            ret = []
        conn.close()
        return(ret)

# obj = wr_scrapeDatabase()
# r = obj.get()
# pass