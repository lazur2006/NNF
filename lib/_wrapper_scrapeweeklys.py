from lib.Scrape_Weeklys import scrapeWeeklys
import sqlite3

class wr_scrapeWeeklys(object):

    def __init__(self, credentials):
        ''' scrape weeklys from HF '''
        self.class_obj = scrapeWeeklys()
        self.class_obj.login(credentials=credentials)
        self.class_obj.account()
        self.class_obj.weeklys()
        self.results = self.class_obj.stream['WEEKLYS']['meals']
        
    def get(self):
        return(self.getDatabaseID([dic['recipe'].get('name') for dic in self.results]))
        
    def getDatabaseID(self,Recipes):
        conn = sqlite3.connect('static/db/recipe.db')
        ID = [conn.execute(
            '''SELECT ID FROM 'RECIPE' WHERE RECIPE_NAME = ?;''',
            (Recipe,)).fetchall() for Recipe in Recipes if Recipe]
        conn.close()
        len_ID = len(ID)
        ''' Drop empty cells '''
        ID = [id for id in ID if id]
        missed_recipes = True if len_ID != len(ID) else False

        return(tuple([id[0] for id in list(zip(*ID))[0]]))
    
    
    
    
    
        
