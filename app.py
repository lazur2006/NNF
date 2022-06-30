import secrets
import operator
import logging
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, make_response
from flask_classful import FlaskView, route
from lib._wrapper_scrapedatabase import wr_scrapeDatabase
from lib.Scrape_Recipes import Thread
from lib.user import user
from lib.vendor import vendor
from lib.qr import QR
from lib.cards import create_cards
from lib.ordershistory import ordershistory
from lib.basket import basket_manager
from lib.favorites import favorites_manager
from lib.search import search

import time
import numpy as np

app = Flask(__name__)

class WebView(FlaskView):
    route_base = '/'
    global recipes
    global basket_ids
    global thread
    global basket_items
    global cards_ids
    recipes = []
    basket_ids = ()
    basket_items = []
    cards_ids = []
        
    @classmethod
    def _init(self):
        global recipes
        global basket_ids
        
        self.obj_scrapeweeklys = []
        self.obj_scrapedatabase = wr_scrapeDatabase()
        recipes = self.obj_scrapedatabase.get_random(limit=10)
        self.recipeNames = self.obj_scrapedatabase.get_allNames()
        self.user = user()
        self.vendor = vendor()
        self.QR = QR()
        self.create_cards = create_cards()
        self.ordershistory = ordershistory()
        self.basket_manager = basket_manager()
        self.favorites_manager = favorites_manager()
        self.search = search()

        print(" :: WebView :: successfully passed")

    @route('/')
    def index(self):
        global recipes

        print(" :: index :: successfully passed")
        tags = self.recipeNames


        return(render_template('index.html',
                               tags=tags,
                               r_name=recipes['recipe_title'],
                               r_subtitle=recipes['recipe_subtitle'],
                               filename=recipes['recipe_img'],
                               r_type=recipes['recipe_type'],
                               r_subtype=recipes['recipe_tag'],
                               r_id=recipes['recipe_id'],
                               r_fav_status= [self.favorites_manager.get_fav_status(e) for e in recipes['recipe_id']],
                               amount=len(recipes['recipe_title'])
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

    @route('/orders', methods=['GET'])
    def orders(self):
        return(render_template('orders.html',data = self.ordershistory.get()))

    def handle_basket_action_relative_ids(self,retval):
        global recipes
        global basket_ids
        global basket_items

        try:
            ''' Try getting new basket elements '''
            retval = operator.itemgetter(*list(map(int, retval.get('Recipes'))))(recipes['recipe_id'])
            ''' Adding them to the existing basket items '''
            basket_ids = basket_ids + (retval if isinstance(retval,tuple) else (retval,))
            basket_ids = tuple(np.unique(basket_ids))
        except:
            pass

        basket_items = self.basket_manager.modify(basket_ids)
        return(basket_items)
    
    def handle_basket_action_absolute_ids(self,retval):
        global recipes
        global basket_ids
        global basket_items

        try:
            ''' Adding them to the existing basket items '''
            basket_ids = basket_ids + tuple([e for e in retval])
            basket_ids = tuple(np.unique(basket_ids))
        except:
            pass

        basket_items = self.basket_manager.modify(basket_ids)
        return(basket_items)

    @route('/', methods=['POST'])
    def post_route(self):
        global recipes
        global basket_ids
        global basket_items
        global cards_ids

        retval = request.get_json()
        route = retval.get('Route')

        if route == 'basket':
            if retval.get('Recipes') or basket_ids:
                basket_items = self.handle_basket_action_relative_ids(retval)                
            else:
                basket_items = []
            return(make_response(jsonify(basket_items), 201))
        elif route == 'clearBasket':
            basket_ids = ()
            basket_items = []
            return(make_response(jsonify(basket_items), 201))
        elif route == 'deleteItem':
            basket_list = list(basket_ids)
            basket_list.remove(retval.get('deleteItem'))
            basket_ids = tuple(basket_list)
            retval["Recipes"] = basket_list
            basket_items = self.handle_basket_action_relative_ids(retval)
            return(make_response(jsonify(basket_items), 201))
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
            return(make_response(jsonify(self.vendor.handleCheckout(ingredients=basket_items,vendor=retval.get('vendor'))), 200))
        elif route == 'mod':
            return(make_response(jsonify(self.vendor.modify_basket(idx=retval.get('idx'),fnc=retval.get('f'))), 200))
        elif route == 'push_vendor_basket':
            self.ordershistory.set(basket_ids)
            return(make_response(jsonify({'status':'ok','missing':self.vendor.push_basket(retval.get('vendor'))['missing']}), 200))
        elif route == 'getCurrentUserStatus':
            return(make_response(jsonify(self.vendor.early), 200))
        elif route == 'create_cards':
            self.ordershistory.set(basket_ids)
            cards_ids = basket_ids
            return(redirect(url_for('WebView:cards')))
        elif route == 'ordershistory_basket':
            self.handle_basket_action_absolute_ids(self.ordershistory.get_recipe_ids(retval['basket_uid']))
            return(redirect(url_for('WebView:index')))
        elif route == 'ordershistory_delete':
            self.ordershistory.delete_item(retval['basket_uid'])
            return(redirect(url_for('WebView:index')))
        elif route == 'ordershistory_cards':
            cards_ids = self.ordershistory.get_recipe_ids(retval['basket_uid'])
            return(redirect(url_for('WebView:cards')))
        elif route == 'logout':
            self.vendor.logout()
            return(make_response(jsonify({'none':'none'}), 200))
        elif route == 'favorite_set':
            self.favorites_manager.set(retval['recipe_id'])
            return(make_response(jsonify({'none':'none'}), 200))
        elif route == 'favorite_unset':
            self.favorites_manager.unset(retval['recipe_id'])
            return(make_response(jsonify({'none':'none'}), 200))
        elif route == 'search_autocomplete_action':
            return(make_response(jsonify(self.search.search_autocomplete_action(retval.get('query'))), 200))

    @route('/choose', methods=['POST'])
    def post_route_choose(self):
        global recipes
        global basket_ids

        route = dict(request.form)['btn']

        if route == 'random':
            recipes = self.obj_scrapedatabase.get_random(limit=int(dict(request.form)['range']))
        if route == 'recent':
            if not self.obj_scrapeweeklys:
                self.obj_scrapeweeklys = self.vendor.handleWeeklys()
            recipes = self.obj_scrapedatabase.get_byID(self.obj_scrapeweeklys.get())
            pass
        if route == 'btn_favorites_show':
            recipes = self.obj_scrapedatabase.get_byID(self.favorites_manager.get_fav_recipe_ids())
        if route == 'search_action':
            recipes = self.search.search_by_ingredient(dict(request.form).get('query'))

        return(redirect(url_for('WebView:index')))

    @route('/cards')
    def cards(self):
        global cards_ids
        global basket_items
        return(render_template('cards.html',data=self.create_cards.get(cards_ids),basket_items=basket_items))

    @route('/favorites')
    def favorites(self):
        return(render_template('favorites.html'))

@app.route('/progress')
def progress():
    global thread

    ''' args : start or retrieve '''
    args = request.args['type']

    def generate():
        while thread.is_alive():
            perc = int((100*thread._tqdmObj.tq.n)/(thread._tqdmObj.tq.total+1))
            yield "data:" + str(perc) + "\n\n"
            time.sleep(0.1)
            if not thread._isRunning:
                yield "data:" + str(100) + "\n\n"

    if(args == 'start'):
        ''' start updater from here '''
        if 'thread' in globals():
            ''' thread object allready created '''
            if not thread.is_alive():
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
            if thread.is_alive():
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
    app.run(debug=True, host=QR.get_ip(), port="8888")
    
    
