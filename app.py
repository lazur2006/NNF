import secrets
import operator
import logging
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, make_response
from flask_classful import FlaskView, route
from lib._wrapper_scrapedatabase import wr_scrapeDatabase
from lib._wrapper_scrapeweeklys import wr_scrapeWeeklys
from lib.Scrape_Recipes import Thread
import sqlite3
import time
import numpy as np
from future.builtins.misc import isinstance

app = Flask(__name__)

credentials = ["kai-schiffer@web.de","datpaM-dogxus-jofte3"]

'''    NOTES
            #SELECT * FROM 'RECIPE' WHERE RECIPE_LABEL='' ORDER BY RANDOM() LIMIT 10
            #SELECT * FROM 'INSTRUCTIONS' WHERE UID = '15'
            #SELECT * FROM 'RECIPE' WHERE RECIPE_LABEL = 'fresh summer'
'''

class WebView(FlaskView):
    route_base = '/'
    global recipes
    global basket
    recipes = []
    basket = ()
    
    def __init__(self):
        global recipes
        global basket
        
        self.obj_scrapeweeklys = []
        self.obj_scrapedatabase = wr_scrapeDatabase()
        recipes = self.obj_scrapedatabase.get_random(limit=10)
        self.recipeNames = self.obj_scrapedatabase.get_allNames()
        

    @route('/')
    def index(self):
        global recipes
        
        tags = self.recipeNames
    
        return(render_template('index.html',
                               tags=tags,
                               r_name=recipes[0],
                               r_subtitle=recipes[1],
                               filename=recipes[2],
                               r_type=recipes[3],
                               r_subtype=recipes[4],
                               amount=len(recipes[0])
                               ))
        
    @route('/login')
    def login(self):
        return(render_template('login.html'))
    
    @route('/settings')
    def settings(self):
        return(render_template('settings.html'))
    
    @route('/checkout')
    def checkout(self):
        data = {'file_name': 'dd', 'set_min': 'hello world 1','rep_sec':'hello world 2'}
        return(render_template('checkout.html',data = data))
    
    @route('/', methods=['POST'])
    def post_route(self):
        global recipes
        global basket
        
        ret = request.get_json()
        route = ret.get('Route')
        
        if route == 'basket':
            if ret.get('Recipes') or basket:
                try:
                    ''' Try getting new basket elements '''
                    ret = operator.itemgetter(*list(map(int, ret.get('Recipes'))))(recipes[5])
                    ''' Adding them to the existing basket items '''
                    basket = basket + (ret if isinstance(ret,tuple) else (ret,))
                    basket = tuple(np.unique(basket))
                except:
                    ''' Otherwise no new elements to add. Pass with existing elements '''
                    pass
                    
                conn = sqlite3.connect('static/db/recipe.db')
                if len(basket) != 1:
                    query = (f"""SELECT RECIPE.RECIPE_NAME, INGREDIENTS.AMOUNT,INGREDIENTS.UNIT,INGREDIENTS.INGREDIENT as INGREDIENT
                    FROM RECIPE
                    JOIN INGREDIENTS ON RECIPE.ID = INGREDIENTS.UID
                    WHERE INGREDIENTS.UID in {basket} ORDER BY INGREDIENT;""")
                else:
                    query = (f"""SELECT RECIPE.RECIPE_NAME, INGREDIENTS.AMOUNT,INGREDIENTS.UNIT,INGREDIENTS.INGREDIENT as INGREDIENT
                    FROM RECIPE
                    JOIN INGREDIENTS ON RECIPE.ID = INGREDIENTS.UID
                    WHERE INGREDIENTS.UID in ({basket[0]}) ORDER BY INGREDIENT;""")
                Ingredients =  conn.execute(query).fetchall()
                Ingredients = list(map(list, zip(*Ingredients)))#[2:5]
                Ingredients[0] = list(dict.fromkeys(Ingredients[0]))
                
                #Ingredients = [[],['2','3','4','5'],["Stk","St","Stk","Stk"],["APFEL","APFEL","BANANE","APFEL"]]
                
                Ingredients[1] = [0.0 if x=='None' else x for x in Ingredients[1]]
                Ingredients[1] = list(map(float, Ingredients[1]))
                Ingredients[3], unq_inv, _ = np.unique(Ingredients[3], return_inverse=True, return_counts=True)
                Ingredients[1] = [sum(np.array(Ingredients[1])[(unq_inv==idx[0])]) for idx in enumerate(Ingredients[3])]
                Ingredients[2] = [np.array(Ingredients[2])[(unq_inv==idx[0])][0] for idx in enumerate(Ingredients[3])]
                
                Ingredients[1] = list(map(float, Ingredients[1]))
                Ingredients[3] = Ingredients[3].tolist()

                
                conn.close()
            else:
                Ingredients = []
            
            pass
        
        elif route == 'clearBasket':
            basket = ()
            Ingredients = []
        
        return(make_response(jsonify(Ingredients), 201))
    
    @route('/choose', methods=['POST'])
    def post_route_choose(self):
        global recipes
        global basket
        
        route = request.form['btn']
        
        if route == 'random':
            recipes = self.obj_scrapedatabase.get_random(limit=int(request.form.getlist('range')[0]))
        if route == 'recent':
            if not self.obj_scrapeweeklys:
                self.obj_scrapeweeklys = wr_scrapeWeeklys(credentials = credentials)
            recipes = self.obj_scrapedatabase.get_byID(self.obj_scrapeweeklys.get())
            pass
        
        return(render_template('index.html',
                               r_name=recipes[0],
                               r_subtitle=recipes[1],
                               filename=recipes[2],
                               r_type=recipes[3],
                               r_subtype=recipes[4],
                               amount=len(recipes[0])
                               ))
    
@app.route('/progress')
def progress():
    
    ''' start updater from here '''
    thread = Thread()
    thread.start()    
    
    def generate():
        x = 0
        
        while thread._isRunning:
            perc = int((100*thread._tqdmObj.tq.n)/thread._tqdmObj.tq.total)
            yield "data:" + str(perc-1) + "\n\n"
            x = x + 1
            time.sleep(0.5)
        if not thread._isRunning:
            yield "data:" + str(100) + "\n\n"
            thread.stop()

    return Response(generate(), mimetype= 'text/event-stream')

WebView.register(app)

if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.secret_key = secrets.token_hex()
    app.run(debug=True, host='192.168.0.10')
