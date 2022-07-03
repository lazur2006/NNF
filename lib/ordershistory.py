import datetime
import sqlite3
from lib._wrapper_scrapedatabase import wr_scrapeDatabase

class ordershistory(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.wr_scrapeDatabase = wr_scrapeDatabase()

    def set(self,basket):
        ''' create SQlite db file '''
        conn = sqlite3.connect('static/db/ordershistory.db')

        today = datetime.date.today()
        _, cw, _ = today.isocalendar()

        try:
            conn.execute("CREATE TABLE ORDERSHISTORY (BASKET_UID INTEGER NOT NULL, DATE TEXT NOT NULL, CW TEXT NOT NULL, RECIPE TEXT NOT NULL);")
        except:
            ''' Already created '''
            pass

        recent_id = conn.execute("SELECT max(BASKET_UID) FROM ORDERSHISTORY;").fetchall()[0][0]
        recent_id = recent_id if recent_id is not None else 0

        ''' Try insert the values '''
        for e in basket:
            conn.execute("INSERT INTO ORDERSHISTORY (BASKET_UID, DATE, CW, RECIPE) VALUES (?,?,?,?)",(recent_id+1,today,cw,str(e)))  


        conn.commit()
        conn.close()

    def get(self):
        ''' create SQlite db file '''

        try:
            conn = sqlite3.connect('static/db/ordershistory.db')

            # get all IDs
            ids = [id[0] for id in conn.execute("SELECT DISTINCT BASKET_UID FROM ORDERSHISTORY;").fetchall()]
            recipe_ids = [[h[0] for h in conn.execute("SELECT RECIPE FROM ORDERSHISTORY WHERE BASKET_UID is (?);",(e,)).fetchall()]for e in ids]

            retval = [{
                "basket_uid":e,
                "date":conn.execute("SELECT DATE FROM ORDERSHISTORY WHERE BASKET_UID is (?);",(e,)).fetchall()[0][0],
                "cw":conn.execute("SELECT CW FROM ORDERSHISTORY WHERE BASKET_UID is (?);",(e,)).fetchall()[0][0],
                "recipes":self.wr_scrapeDatabase.get_byID(recipe_ids[idx])
                    } for idx,e in enumerate(ids)]

            conn.close()
            if not ids:
                retval = {"basket_uid":"exception"}
        except:
            retval = {"basket_uid":"exception"}


        return(retval)

    def get_recipe_ids(self,basket_uid):
        conn = sqlite3.connect('static/db/ordershistory.db')
        retval = tuple([int(e[0]) for e in conn.execute("SELECT RECIPE FROM ORDERSHISTORY WHERE BASKET_UID is (?);",(basket_uid,)).fetchall()])
        conn.close()
        return(retval)

    def delete_item(self,basket_uid):
        conn = sqlite3.connect('static/db/ordershistory.db')
        conn.execute("DELETE FROM ORDERSHISTORY WHERE BASKET_UID=(?);",(basket_uid,))
        conn.commit()
        conn.close()