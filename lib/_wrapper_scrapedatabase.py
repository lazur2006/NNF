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
            return(self.__get(f"SELECT * FROM 'RECIPE' WHERE ID IN {tuple(ID)} ORDER BY ID LIMIT(300);"))
        else:
            return(self.__get(f"SELECT * FROM 'RECIPE' WHERE ID IN ({ID[0]}) ORDER BY ID LIMIT(300);"))
    
    def get_allNames(self):
        conn = sqlite3.connect('static/db/recipe.db')
        try:
            ret = conn.execute("SELECT RECIPE_NAME FROM 'RECIPE'").fetchall()
            ret = list(list(zip(*ret))[0])
        except:
            ret = []
        conn.close()
        return(ret)

    def get_by_tag(self,tag):
        conn = sqlite3.connect('static/db/recipe.db')
        ret = self.get_byID([e[0] for e in conn.execute("SELECT UID FROM 'TAGS' WHERE TAG = ?;",(tag,)).fetchall()])
        conn.close()
        return(ret)

    def get_all_tags(self):
        conn = sqlite3.connect('static/db/recipe.db')
        try:
            ret = [e[0] for e in conn.execute("SELECT DISTINCT TAG FROM 'TAGS'").fetchall()]
        except:
            ret = []
        conn.close()
        return(ret)

    def search_autocomplete_action(self,query):
        conn = sqlite3.connect('static/db/recipe.db')
        retval = {'found_ingredients':
        [e[0] for e in conn.execute("SELECT DISTINCT INGREDIENT FROM 'INGREDIENTS' WHERE INGREDIENT LIKE (?)",('%' + query + '%',)).fetchall()]}
        conn.close()
        return(retval)

    def search_by_ingredient(self,ingredient_list):
        conn = sqlite3.connect('static/db/recipe.db')
        #retval = self.wr_scrapeDatabase.get_byID([(e[0]) for e in conn.execute("SELECT DISTINCT UID FROM 'INGREDIENTS' WHERE INGREDIENT = (?)  LIMIT(52)",(ingredient,)).fetchall()])
        #and search query
        query=f"""SELECT UID FROM 'INGREDIENTS' WHERE INGREDIENT IN {tuple(ingredient_list) if len(ingredient_list)>1 else "('"+ingredient_list[0]+"')"} GROUP BY UID HAVING COUNT(*) > {len(ingredient_list)-1}"""
        retval = self.get_byID([(e[0]) for e in conn.execute(query).fetchall()])
        conn.close()
        return(retval)

    def count_search_by_ingredient(self,ingredient_list):
        conn = sqlite3.connect('static/db/recipe.db')
        if ingredient_list:
            query=f"""SELECT UID FROM 'INGREDIENTS' WHERE INGREDIENT IN {tuple(ingredient_list) if len(ingredient_list)>1 else "('"+ingredient_list[0]+"')"} GROUP BY UID HAVING COUNT(*) > {len(ingredient_list)-1}"""
            retval = len(conn.execute(query).fetchall())
        else:
            retval = 0
        conn.close()
        return(retval)