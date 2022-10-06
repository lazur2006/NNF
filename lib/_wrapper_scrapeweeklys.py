from lib.Scrape_Weeklys import scrapeWeeklys
from lib.user import user
import sqlite3
import datetime

class wr_scrapeWeeklys(object):

    def __init__(self, credentials):
        ''' scrape weeklys from HF '''
        self.class_obj = scrapeWeeklys()
        self.class_obj.login(credentials=credentials)
        self.class_obj.account()
        self.class_obj.weeklys()
        self.results = self.class_obj.stream['WEEKLYS']
        self.user = user()
        
    def get(self):
        _, week_num, _ = datetime.date.today().isocalendar()
        if week_num != self.class_obj.week_num:
            self.repeat_access()
        return(self.getDatabaseID(self.results))
        
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

        try:
            return(tuple([id[0] for id in list(zip(*ID))[0]]))
        except:
            return(())

    def repeat_access(self):
        self.class_obj.login(credentials=[self.user.getCredentials('HelloFresh')['username'],self.user.getCredentials('HelloFresh')['password']])
        self.class_obj.weeklys()
        self.results = self.class_obj.stream['WEEKLYS']
    
    
    
    
    
        
