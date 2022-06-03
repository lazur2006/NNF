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
    
    def get(self,cmd):
        ''' SQlite connection ------------------------------------------ '''
        
        ''' create SQlite db file '''
        conn = sqlite3.connect('static/db/recipe.db')
        
        RECIPES = conn.execute(cmd).fetchall()
        RECIPES = list(map(list, zip(*RECIPES)))
        
        INGREDIENTS = []
        INSTRUCTIONS = []
        TAGS = []
        for i in range(len(RECIPES[0])):
            arg = conn.execute('''SELECT * FROM 'INGREDIENTS' WHERE UID=?;''',(RECIPES[0][i],)).fetchall()
            INGREDIENTS.append(list(map(list, zip(*arg))))

            arg = conn.execute('''SELECT * FROM 'INSTRUCTIONS' WHERE UID=?;''',(RECIPES[0][i],)).fetchall()
            INSTRUCTIONS.append(list(map(list, zip(*arg))))
            
            arg = conn.execute('''SELECT * FROM 'TAGS' WHERE UID=?;''',(RECIPES[0][i],)).fetchall()
            TAGS.append(list(map(list, zip(*arg))))
        
        
        conn.close()
        
        tags = [self.safe_list_get(t, 2, ['']) for t in TAGS]
        tags = list(list(zip(*tags))[0])
        
        array_recipes_sep = [RECIPES[1],
                             RECIPES[3],
                             ["static/images/de-DE/" + str(s) + ".jpg" for s in RECIPES[0]],
                             tags,
                             RECIPES[4],
                             RECIPES[0]
                              ]
        ''' unzip array in terms of combined to types'''
        return(array_recipes_sep)
     
    def get_random(self,limit):
        return(self.get(f"SELECT * FROM 'RECIPE' ORDER BY RANDOM() LIMIT {limit};"))
    
    def get_byID(self,ID):
        return(self.get(f"SELECT * FROM 'RECIPE' WHERE ID IN ({','.join([str(e[0]) for e in ID[0]])}) ORDER BY ID;"))
    
    def get_allNames(self):
        conn = sqlite3.connect('static/db/recipe.db')
        ret = conn.execute("SELECT RECIPE_NAME FROM 'RECIPE'").fetchall()
        ret = list(list(zip(*ret))[0])
        conn.close()
        return(ret)

# obj = wr_scrapeDatabase()
# r = obj.get()
# pass