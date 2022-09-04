import sqlite3


class favorites_manager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        ''' create SQlite db file '''
        conn = sqlite3.connect('static/db/favorites.db')
        try:
            conn.execute("CREATE TABLE FAVORITES (RECIPE_UID TEXT NOT NULL, UNIQUE(RECIPE_UID));")
        except:
            ''' Already created '''
            pass
        conn.commit()
        conn.close()

    def get_recipe_uid(self,recipe_id):
        conn = sqlite3.connect('static/db/recipe.db')
        retval = conn.execute("SELECT RECIPE_UID FROM RECIPE WHERE ID is (?);",(recipe_id,)).fetchall()[0][0]
        conn.close()
        return(retval)

    def get_recipe_id(self,recipe_uid):
        conn = sqlite3.connect('static/db/recipe.db')
        try:
            retval = conn.execute("SELECT ID FROM RECIPE WHERE RECIPE_UID is (?);",(recipe_uid,)).fetchall()[0][0]
        except:
            retval = []
        conn.close()
        return(retval)

    def set(self,recipe_id):
        conn = sqlite3.connect('static/db/favorites.db')
        ''' Try insert the values '''
        conn.execute("INSERT OR IGNORE INTO FAVORITES (RECIPE_UID) VALUES (?)",(self.get_recipe_uid(recipe_id),))
        conn.commit()
        conn.close()

    def unset(self,recipe_id):
        conn = sqlite3.connect('static/db/favorites.db')
        conn.execute("DELETE FROM FAVORITES WHERE RECIPE_UID=(?);",(self.get_recipe_uid(recipe_id),))
        conn.commit()
        conn.close()

    def get_fav_status(self,recipe_id):
        #recipe_uid = self.get_recipe_uid(recipe_id)
        conn = sqlite3.connect('static/db/favorites.db')
        try:
            retval = conn.execute("SELECT COUNT(RECIPE_UID) FROM FAVORITES WHERE RECIPE_UID = ?;",(self.get_recipe_uid(recipe_id),)).fetchall()[0][0]
        except:
            retval = []
        conn.close()
        if(bool(retval)):
            return('text-danger')
        else:
            return('text-secondary')

    def get_fav_recipe_ids(self):
        conn = sqlite3.connect('static/db/favorites.db')
        retval = tuple([self.get_recipe_id(e[0]) for e in conn.execute("SELECT RECIPE_UID FROM FAVORITES;").fetchall()])
        conn.close()
        return(retval)