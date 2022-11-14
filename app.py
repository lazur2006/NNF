#!/usr/bin/env python
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
from lib.git_manager import git_manager
import time
import numpy as np
from urllib.parse import quote

app = Flask(__name__)
app.jinja_env.filters['quote_plus'] = lambda u: quote(u)

class static(object):
    recipes, basket_items, basket_ids, cards_ids, frun = [], [], (), [], False

class WebView(FlaskView):
    route_base = '/'

    def __init__(self) -> None:
        super().__init__()
        if not static.frun:
            static.frun = True
            self.handle_recipes('handle_recipe_action_get_randoms',16)
            print(" :: __INIT__ :: ")

    @classmethod
    def pre_init(self):
        self.obj_scrapeweeklys = []
        self.obj_scrapedatabase = wr_scrapeDatabase()
        self.recipeNames = self.obj_scrapedatabase.get_allNames()
        self.user = user()
        self.vendor = vendor()
        self.QR = QR()
        self.create_cards = create_cards()
        self.ordershistory = ordershistory()
        self.basket_manager = basket_manager()
        self.favorites_manager = favorites_manager()
        self.git_manager = git_manager()
        print(" :: SERVER STARTED :: ")

    @route('/')
    def index(self):

        retval = self.handle_recipes('return_recipes')

        print(" :: index :: successfully passed")
        tags = self.obj_scrapedatabase.get_all_tags()

        return(render_template('index.html',
                               tags=tags,
                               r_name=retval['recipe_title'],
                               r_subtitle=retval['recipe_subtitle'],
                               filename=retval['recipe_img'],
                               r_type=retval['recipe_type'],
                               r_subtype=retval['recipe_tag'],
                               r_id=retval['recipe_id'],
                               r_fav_status= [self.favorites_manager.get_fav_status(e) for e in retval['recipe_id']],
                               amount=len(retval['recipe_title'])
                               ))

    @route('/login')
    def login(self):
        return(render_template('login.html', vendor = enumerate(self.vendor.early.items())))

    @route('/settings')
    def settings(self):
        return(render_template('settings.html'))

    @route('/orders', methods=['GET'])
    def orders(self):
        return(render_template('orders.html',data = self.ordershistory.get()))

    def handle_recipes(self,fcn,val=""):
        if fcn=='handle_recipe_action_get_randoms':
            static.recipes = self.obj_scrapedatabase.get_random(val)
        elif fcn=='handle_recipe_action_get_by_tag':
            static.recipes = self.obj_scrapedatabase.get_by_tag(val)
        elif fcn=='handle_recipe_action_get_by_id':
            static.recipes = self.obj_scrapedatabase.get_byID(val)
        elif fcn=='handle_recipe_action_search_ingredient':
            static.recipes = self.obj_scrapedatabase.search_by_ingredient(val)
        elif fcn=='return_recipes':
            pass
        return(static.recipes)

    def handle_basket(self,fcn,val=""):
        if fcn=='handle_basket_action_relative_ids':#e.g. 1,2,3,4...
            try:
                ''' Try getting new basket elements '''
                val = operator.itemgetter(*list(map(int, val)))(self.handle_recipes('return_recipes')['recipe_id'])
                ''' Adding them to the existing basket items '''
                static.basket_ids = static.basket_ids + (val if isinstance(val,tuple) else (val,))
                static.basket_ids = tuple(np.unique(static.basket_ids))
                static.basket_items = self.basket_manager.build_basket(static.basket_ids)
            except:
                pass
        elif fcn=='handle_basket_action_absolute_ids':#e.g. 1833,3919,2143...
            try:
                ''' Adding them to the existing basket items '''
                static.basket_ids = static.basket_ids + tuple([int(e) for e in val])
                static.basket_ids = tuple(np.unique(static.basket_ids))
                static.basket_items = self.basket_manager.build_basket(static.basket_ids)
            except:
                pass
        elif fcn=='remove_item':
            temp_list = list(static.basket_ids)
            temp_list.remove(val)
            static.basket_ids = tuple(temp_list)
            self.handle_basket('handle_basket_action_absolute_ids',static.basket_ids)
        elif fcn=='clear_basket':
            static.basket_items = []
            static.basket_ids = ()
        elif fcn=='update_basket':
            try:
                static.basket_items = self.basket_manager.build_basket(static.basket_ids)
            except:
                pass
        elif fcn=='return_basket':
            pass

        return(static.basket_items)

    @route('/', methods=['POST'])
    def post_route(self):

        retval = request.get_json()
        route = retval.get('Route')

        if route == 'basket':
            self.handle_basket('handle_basket_action_absolute_ids',request.get_json().get('Recipes'))
            return(make_response(jsonify(self.handle_basket('return_basket')), 201))
        elif route == 'clearBasket':
            self.handle_basket('clear_basket')
            return(make_response(jsonify(self.handle_basket('return_basket')), 201))
        elif route == 'deleteItem':
            self.handle_basket('remove_item',retval.get('deleteItem'))
            return(make_response(jsonify(self.handle_basket('return_basket')), 201))
        elif route == 'saveCredentials':
            self.user.setCredentials(retval.get('vendor'),retval.get('username'),retval.get('password'),retval.get('ipaddress'))
            status = self.vendor.login(retval.get('vendor'))
            info = self.vendor.getUserInfo(retval.get('vendor'))
            return(make_response(jsonify({'vendor':retval.get('vendor'),'status':status,'info':info}), 200))
        elif route == 'checkout':
            return(make_response(jsonify(self.vendor.handleCheckout(ingredients=self.handle_basket('return_basket').get('unique_basket_elements'),vendor=retval.get('vendor'))), 200))
        elif route == 'add_missing':
            return(make_response(jsonify(self.vendor.handleMissingIngredients(), 200)))
        elif route == 'mod':
            return(make_response(jsonify(self.vendor.modify_basket(idx=retval.get('idx'),fnc=retval.get('f'))), 200))
        elif route == 'push_vendor_basket':
            self.ordershistory.set(self.handle_basket('return_basket').get('basket_recipe_elements').get('recipe_id'))
            return(make_response(jsonify({'status':'ok','missing':self.vendor.push_basket(retval.get('vendor'))['missing']}), 200))
        elif route == 'getCurrentUserStatus':
            return(make_response(jsonify(self.vendor.early), 200))
        elif route == 'create_cards':
            self.ordershistory.set(self.handle_basket('return_basket').get('basket_recipe_elements').get('recipe_id'))
            static.cards_ids = tuple(self.handle_basket('return_basket').get('basket_recipe_elements').get('recipe_id'))
            return(redirect(url_for('WebView:cards')))
        elif route == 'ordershistory_basket':
            self.handle_basket('handle_basket_action_absolute_ids',self.ordershistory.get_recipe_ids(retval['basket_uid']))
            return(redirect(url_for('WebView:index')))
        elif route == 'ordershistory_delete':
            self.ordershistory.delete_item(retval['basket_uid'])
            return(redirect(url_for('WebView:index')))
        elif route == 'ordershistory_cards':
            static.cards_ids = self.ordershistory.get_recipe_ids(retval['basket_uid'])
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
            return(make_response(jsonify(self.obj_scrapedatabase.search_autocomplete_action(retval.get('query'))), 200))
        elif route == 'show_recipes_by_tag':
            self.handle_recipes('handle_recipe_action_get_by_tag',retval.get('tag'))
            return(redirect(url_for('WebView:index')))
        elif route=='show_recipes_by_ingredient_search':
            self.handle_recipes('handle_recipe_action_search_ingredient',retval.get('ingredient_list'))
            return(redirect(url_for('WebView:index')))
        elif route=='count_recipes_by_ingredient_search':
            return(make_response(jsonify(self.obj_scrapedatabase.count_search_by_ingredient(retval.get('ingredient_list'))), 200))
        elif route=='handle_update_app_action':
            return(make_response(jsonify(self.git_manager.update_available()), 200))
        elif route=='start_application_update':
            self.git_manager.update_repository()
            return(make_response(jsonify({'':''}), 200))
        elif route=='modify_recipe_portions':
            self.basket_manager.modify_recipe_portions(retval.get('f'))
            return(make_response(jsonify({'num_recipe_portions':self.basket_manager.get_num_recipe_portions(),'basket':self.handle_basket('update_basket')}), 200))
            

    @route('/choose', methods=['POST'])
    def post_route_choose(self):

        route = dict(request.form)['btn']

        if route == 'random':
            self.handle_recipes('handle_recipe_action_get_randoms',int(dict(request.form)['range']))      
        if route == 'recent':
            if not self.obj_scrapeweeklys:
                self.obj_scrapeweeklys = self.vendor.handleWeeklys()            
            self.handle_recipes('handle_recipe_action_get_by_id',self.obj_scrapeweeklys.get())
        if route == 'btn_favorites_show':
            self.handle_recipes('handle_recipe_action_get_by_id',self.favorites_manager.get_fav_recipe_ids())

        return(redirect(url_for('WebView:index')))

    @route('/cards')
    def cards(self):
        data = self.create_cards.get_basket(static.cards_ids)
        return(render_template('cards.html',data=data.get('cards_data'),basket_items=data.get('cards_overall_ingredients')))

    @route('/favorites')
    def favorites(self):
        return(render_template('favorites.html'))

@app.route('/wake')
def wake_state():
    return(Response("data: close\n\n", mimetype= 'text/event-stream'))

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



WebView.pre_init()
WebView.register(app)

if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    QR = QR()
    app.secret_key = secrets.token_hex()
    app.run(debug=True, host=QR.get_ip(), port="8888")
    
    
