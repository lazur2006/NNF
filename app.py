import secrets
import operator
import logging
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, make_response
from flask_classful import FlaskView, route
from lib._wrapper_scrapedatabase import wr_scrapeDatabase
from lib._wrapper_scrapeweeklys import wr_scrapeWeeklys
from lib.Scrape_Recipes import Thread
from lib.user import user
from lib.vendor import vendor
from lib.qr import QR
import sqlite3
import time
import numpy as np
#import webbrowser

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
    global thread
    global Ingredients
    recipes = []
    basket = ()
    Ingredients = []
        
    @classmethod
    def _init(self):
        global recipes
        global basket
        
        self.obj_scrapeweeklys = []
        self.obj_scrapedatabase = wr_scrapeDatabase()
        recipes = self.obj_scrapedatabase.get_random(limit=10)
        self.recipeNames = self.obj_scrapedatabase.get_allNames()
        self.user = user()
        self.vendor = vendor()
        self.QR = QR()
        
        print(" :: WebView :: successfully passed")
        
        #webbrowser.open(f"http://{self.QR.get_ip()}:5000", new=2)
        

    @route('/')
    def index(self):
        global recipes
        
        print(" :: index :: successfully passed")
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
        
        # vendor = enumerate(self.vendor.early.items())
        #
        # for idx,(vendor_,valid) in vendor:
        #     print(vendor_)
        #     print(valid)
        
        return(render_template('login.html',
                               vendor = enumerate(self.vendor.early.items())))
    
    @route('/settings')
    def settings(self):
        return(render_template('settings.html'))
    
    @route('/orders')
    def orders(self):
        data = {'file_name': 'dd', 'set_min': 'hello world 1','rep_sec':'hello world 2'}
        return(render_template('orders.html',data = data))
    
    def get_json_recipe_feed(self,retval):
        global recipes
        global basket
        global Ingredients
        
        try:
            ''' Try getting new basket elements '''
            retval = operator.itemgetter(*list(map(int, retval.get('Recipes'))))(recipes[5])
            ''' Adding them to the existing basket items '''
            basket = basket + (retval if isinstance(retval,tuple) else (retval,))
            basket = tuple(np.unique(basket))
        except:
            # try:
            #     ''' Elements were deleted try to update the basket '''
            #     if basket > tuple(retval.get('Recipes')):
            #         basket = tuple(retval.get('Recipes'))
            # except:
            #     ''' Otherwise no new elements to add. Pass with existing elements '''
            pass
            
        conn = sqlite3.connect('static/db/recipe.db')
        if len(basket) != 1:
            query = (f"""SELECT RECIPE.ID, RECIPE.RECIPE_NAME, INGREDIENTS.AMOUNT,INGREDIENTS.UNIT,INGREDIENTS.INGREDIENT as INGREDIENT
            FROM RECIPE
            JOIN INGREDIENTS ON RECIPE.ID = INGREDIENTS.UID
            WHERE INGREDIENTS.UID in {basket} ORDER BY INGREDIENT;""")
        else:
            query = (f"""SELECT RECIPE.ID, RECIPE.RECIPE_NAME, INGREDIENTS.AMOUNT,INGREDIENTS.UNIT,INGREDIENTS.INGREDIENT as INGREDIENT
            FROM RECIPE
            JOIN INGREDIENTS ON RECIPE.ID = INGREDIENTS.UID
            WHERE INGREDIENTS.UID in ({basket[0]}) ORDER BY INGREDIENT;""")
        Ingredients =  conn.execute(query).fetchall()
        Ingredients = list(map(list, zip(*Ingredients)))#[2:5]
        Ingredients[0] = list(dict.fromkeys(Ingredients[0]))
        Ingredients[1] = list(dict.fromkeys(Ingredients[1]))
        
        #Ingredients = [[],['2','3','4','5'],["Stk","St","Stk","Stk"],["APFEL","APFEL","BANANE","APFEL"]]
        
        Ingredients[2] = [0.0 if x=='None' else x for x in Ingredients[2]]
        Ingredients[2] = list(map(float, Ingredients[2]))
        Ingredients[4], unq_inv, _ = np.unique(Ingredients[4], return_inverse=True, return_counts=True)
        Ingredients[2] = [sum(np.array(Ingredients[2])[(unq_inv==idx[0])]) for idx in enumerate(Ingredients[4])]
        Ingredients[3] = [np.array(Ingredients[3])[(unq_inv==idx[0])][0] for idx in enumerate(Ingredients[4])]
        
        Ingredients[2] = list(map(float, Ingredients[2]))
        Ingredients[4] = Ingredients[4].tolist()
        
        ret = {"ID":Ingredients[0],
               "Name":Ingredients[1],
               "Amount":Ingredients[2],
               "Unit":Ingredients[3],
               "Ingredient":Ingredients[4]}
        
        Ingredients = ret
        
        conn.close()
        
        return(Ingredients)        
    
    @route('/', methods=['POST'])
    def post_route(self):
        global recipes
        global basket
        global Ingredients
        
        retval = request.get_json()
        route = retval.get('Route')
        
        if route == 'basket':
            if retval.get('Recipes') or basket:
                Ingredients = self.get_json_recipe_feed(retval)                
            else:
                Ingredients = []
            
            
            return(make_response(jsonify(Ingredients), 201))
        elif route == 'clearBasket':
            basket = ()
            Ingredients = []
            return(make_response(jsonify(Ingredients), 201))
        elif route == 'deleteItem':
            basket_list = list(basket)
            basket_list.remove(retval.get('deleteItem'))
            basket = tuple(basket_list)
            retval["Recipes"] = basket_list
            Ingredients = self.get_json_recipe_feed(retval)
            return(make_response(jsonify(Ingredients), 201))
        elif route == 'saveCredentials':
            self.user.setCredentials(
                vendor=retval.get('vendor'), 
                username=retval.get('username'), 
                password=retval.get('password'),
                ipaddress=retval.get('ipaddress')
                )
            status = self.vendor.login(retval.get('vendor'))
            info = self.vendor.getUserInfo(retval.get('vendor'))
            return(make_response(jsonify({'vendor':retval.get('vendor'),'status':status,'info':info}), 200))
        elif route == 'checkout':
            return(make_response(jsonify(self.vendor.handleCheckout(ingredients=Ingredients,vendor=retval.get('vendor'))), 200))
        elif route == 'mod':
            return(make_response(jsonify(self.vendor.modify_basket(idx=retval.get('idx'),fnc=retval.get('f'))), 200))
        elif route == 'push_vendor_basket':
            self.vendor.push_basket(retval.get('vendor'))
            return(make_response(jsonify({'status':'ok'}), 200))
        elif route == 'getCurrentUserStatus':
            return(make_response(jsonify(self.vendor.early), 200))
        
    
    @route('/choose', methods=['POST'])
    def post_route_choose(self):
        global recipes
        global basket
        
        route = list(request.form.values())[1]
        
        if route == 'random':
            recipes = self.obj_scrapedatabase.get_random(limit=int(list(request.form.values())[0]))
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
    global thread
    
    ''' args : start or retrieve '''
    args = request.args['type']
    
    def generate():
        while thread.isRunning():
            perc = int((100*thread._tqdmObj.tq.n)/(thread._tqdmObj.tq.total+1))
            yield "data:" + str(perc) + "\n\n"
            time.sleep(0.1)
            if not thread._isRunning:
                yield "data:" + str(100) + "\n\n"
    
    if(args == 'start'):
        ''' start updater from here '''
        if 'thread' in globals():
            ''' thread object allready created '''
            if not thread.isRunning():
                ''' Prevent restart when thread allready runs '''
                thread = Thread()
                thread.start()
        else:
            ''' thread object not created yet '''
            thread = Thread()
            thread.start()
        retval = generate()
    elif(args == 'retrieve'):
        if 'thread' in globals():
            ''' thread object allready created '''
            if thread.isRunning():
                retval = generate()
            else:
                retval = "data: close\n\n"
        else:
            retval = "data: close\n\n"
    
    return Response(retval, mimetype= 'text/event-stream')


WebView._init()
WebView.register(app)

if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    QR = QR()
    app.secret_key = secrets.token_hex()
    app.run(debug=True, host=QR.get_ip())
    
