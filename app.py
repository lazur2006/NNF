import secrets
import operator
import logging
from flask import Flask, render_template, request, redirect, url_for
from flask_classful import FlaskView, route
from lib._wrapper_demo import wr_demo
from lib._wrapper_scrapedatabase import wr_scrapeDatabase

app = Flask(__name__)


class WebView(FlaskView):
    route_base = '/'
    
    def __init__(self):
        # try:
        #     self.obj_scrapeweeklys = wr_scrapeWeeklys(
        #         credentials=["kai-schiffer@web.de", "datpaM-dogxus-jofte3"]
        #         )
        # except:
        #     pass
        self.obj_demo = wr_demo()
        self.obj_scrapedatabase = wr_scrapeDatabase()
        #r = self.obj_scrapeweeklys.get()
        #r = self.obj_demo.get()
        self.r = self.obj_scrapedatabase.get()
        self.r=[i[1:25] for i in self.r]

    @route('/')
    def index(self):
        return(render_template('index.html',
                               r_name=self.r[0],
                               r_subtitle=self.r[1],
                               filename=self.r[2],
                               r_type=self.r[3],
                               r_subtype=self.r[4],
                               amount=len(self.r[0])
                               ))
        
    @route('/login')
    def login(self):
        return(render_template('login.html'))
    
    @route('/', methods=['POST'])
    def post_route(self):
        
        route = request.form['btn']
        
        if route == 'basket':
            self.callback_basket()
            pass
        if route == 'random':
            self.callback_random()
            pass
        if route == 'recent':
            self.callback_recent()
            pass
        
        return(redirect(url_for('WebView:index')))
    
    def callback_basket(self):
        print("basket")
        selected = list(map(int, request.form.getlist('c_checkboxField')))
        if selected:
            recipes_selected = operator.itemgetter(*selected)(self.r[0])
            recipes_selected = list(recipes_selected) if isinstance(recipes_selected, tuple) else [recipes_selected]
            
            for recipe in recipes_selected:
                print("Selected recipe: " + recipe)

    def callback_random(self):
        print("random")
        pass
    
    def callback_recent(self):
        print("recent")
        pass

WebView.register(app)

if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.secret_key = secrets.token_hex()
    app.run(debug=True, host='192.168.0.10')
