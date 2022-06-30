import sqlite3
from lib._wrapper_scrapedatabase import wr_scrapeDatabase

class search(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.wr_scrapeDatabase = wr_scrapeDatabase()

    def search_autocomplete_action(self,query):

        ''' create SQlite db file '''
        conn = sqlite3.connect('static/db/recipe.db')
        retval = {'found_ingredients':
        [e[0] for e in conn.execute("SELECT DISTINCT INGREDIENT FROM 'INGREDIENTS' WHERE INGREDIENT LIKE (?)",(query + '%',)).fetchall()]}
        conn.close()
        return(retval)

    def search_by_ingredient(self,ingredient):
        ''' create SQlite db file '''
        conn = sqlite3.connect('static/db/recipe.db')
        retval = self.wr_scrapeDatabase.get_byID([(e[0]) for e in conn.execute("SELECT DISTINCT UID FROM 'INGREDIENTS' WHERE INGREDIENT = (?)  LIMIT(52)",(ingredient,)).fetchall()])
        conn.close()
        return(retval)