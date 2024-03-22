import requests
import re
import urllib.request
import time
import base64
from tqdm import tqdm
#from PyQt5.QtCore import QThread, pyqtSignal
import threading
import sqlite3
import brotli


import ssl
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_
ciphers = (
'''ECDHE-ECDSA-AES128-GCM-SHA256:'''
'''ECDHE-RSA-AES128-GCM-SHA256:'''
'''ECDHE-ECDSA-AES256-GCM-SHA384:'''
'''ECDHE-RSA-AES256-GCM-SHA384:'''
'''ECDHE-ECDSA-CHACHA20-POLY1305:'''
'''ECDHE-RSA-CHACHA20-POLY1305:'''
'''DHE-RSA-AES128-GCM-SHA256:'''
'''DHE-RSA-AES256-GCM-SHA384'''
)

host = "https://gw.hellofresh.com"
salt = "hellofresh-ios-customer:ca154f43-687b-4866-9d4e-a618f42da8c9"

class TLSAdapter(HTTPAdapter):

    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super(TLSAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ctx = ssl_.create_urllib3_context(ciphers=ciphers, 
                                          cert_reqs=ssl.CERT_REQUIRED, 
                                          options=self.ssl_options)
        self.poolmanager = PoolManager(*pool_args,
                                       ssl_context=ctx,
                                       **pool_kwargs)

class TQDM:
    def __init__(self,r):
        self.tq=tqdm(r)
    
    def remaining(self):
        rate = self.tq.format_dict["rate"]
        remaining = (self.tq.total - self.tq.n) / rate if rate and self.tq.total else 0  # Seconds*        
        remaining = time.strftime('%H:%M:%S', time.gmtime(remaining))
        return remaining    

class Thread(threading.Thread):
    #_signal = ""#pyqtSignal(int)
    #_state_msg = ""#pyqtSignal('QString')
    #_max = ""#pyqtSignal(int)
    def __init__(self):
        super(Thread, self).__init__()
        self._isRunning = True
        self._tqdmObj = TQDM(range(1))

        self.session = requests.session()
        self.adapter = TLSAdapter(ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TICKET)
        self.session.mount("https://", self.adapter)

    def __del__(self):
        self.wait()
        
    def stop(self):
        self._isRunning = False
        
    def auth(self):
        url = f"{host}/auth/token?locale=de-DE&country=DE"
        payload = "grant_type=client_credentials&scope=public"
        headers = {
          'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
          'user-agent': 'HelloFresh/22.8 (com.hellofresh.HelloFresh; build:4616773; iOS 14.6.0) Alamofire/5.4.4',
          'authorization': f'Basic {str(base64.b64encode(salt.encode("ascii")), "utf-8")}'
        }
        
        return(self.session.request("POST", url, headers=headers, data=payload).json()['access_token'])

    def run(self):
        
        # run thread while flag is True
        while self._isRunning:
            # create new session
            session = requests.Session()
            
            # HelloFresh URL
            # url = f"{host}/api/recipes/search?"

            

            payload = {}
            headers = {
            'host': 'gw.hellofresh.com',
            'accept': '*/*',
            'connection': 'keep-alive',
            'user-agent': 'HelloFresh/24.12 (com.hellofresh.HelloFresh; build:6703464; iPhone 16.7.4) HFNetworking',
            'authorization': f"Bearer {self.auth()}",
            'accept-language': 'de-DE,de;q=0.9',
            'accept-encoding': 'gzip, deflate, br'
            }
            
            # maximum items to return are 250
            limit = 100
            # take only recipes in consideration if there ingredient amount is more than 3
            minIngredientAmount = 3
            # Should also are the images saved?
            saveFiles=True
            
            LOCALE=["de-DE","en-US"]
            COUNTRY=["de","us"]
            
            locale=LOCALE[0]
            country=COUNTRY[0]
            
            # payload={
            #   "offset": "0",
            #   "limit": str(limit),
            #   "locale": locale,
            #   "country": country
            # }
            
            #self._state_msg.emit("Get fresh bearer auth token...")
            # apply bearer
            # headers = {
            #   'Authorization': f"Bearer {self.auth()}"
            #   }

            url = f"https://gw.hellofresh.com/recipes/recipes/search?country=de&locale=de-DE&not-author=thermomix&offset=0&limit=10"

            # "https://gw.hellofresh.com/recipes/recipes/search?country=de&locale=de-DE&limit=10&not-author=thermomix&offset=0&order=-date"
            
            # find out how many recipes are present (only german DE market)
            try:
                response = session.request("GET", url, headers=headers, params=payload, timeout=2)
            except:
                response.status_code = 503
            cnt = 0
            while response.status_code == 503 and cnt < 5:
                        try:
                            response = session.request("GET", url, headers=headers, params=payload, timeout=2)
                        except:
                            response.status_code = 503
                        cnt = cnt + 1
            response = response.json()
            total = response['total']
            iterations = int(response['total']/limit)
            residuals = response['total']%limit
            print(">> Found a total of",total,"HelloFresh recipes")
            
            # Because max 250 recipes can be loaded, 
            # a iteration about all recipes should be started
            if residuals>0:
                iterations=iterations+1
            recipes=[]
            offset = 0
            self._tqdmObj = TQDM(range(iterations))
            for i in self._tqdmObj.tq:
                if not self._isRunning:
                    break
                #self._max.emit(iterations)
                #self._signal.emit(i)
                #self._state_msg.emit("Step 1/8\n\nDownload "+str(i)+" of "+str(iterations)+" packages server\n\nRemaining Time "+self._tqdmObj.remaining())
                # payload={
                #     "offset": str(offset),
                #     "limit": str(limit),
                #     "locale": locale,
                #     "country": country
                # }
                url = f"https://gw.hellofresh.com/recipes/recipes/search?country=DE&locale=de-DE&not-author=thermomix&offset={offset}&limit={limit}"
                offset += limit
                try:
                    response = session.request("GET", url, headers=headers, params=payload, timeout=2)
                    timeout = False
                except:
                    response.status_code = 503
                    timeout = True
                cnt = 0
                if response.status_code == 503 or timeout:
                    print("503 detected ... do max 5 retries")
                    while response.status_code == 503 or response.status_code == 500 and cnt < 5:
                        try:
                            response = session.request("GET", url, headers=headers, params=payload, timeout=2)
                        except:
                            response.status_code = 503
                        cnt = cnt + 1
                try:
                    recipes.extend(response.json()['items'])
                except Exception as e:
                    print(e)
                    break
                    # pass
            
            # Drop recipes when
            # - ingredients list is empty
            # - thermomix classified
            # - ingredients amount less than "minIngredientAmount"
            recipesFiltred=[]
            recipesOutsourced=[]
            for i in range(len(recipes)):
                if not self._isRunning:
                    break
                try:
                    # if(any(recipes[i]['ingredients']) and recipes[i]['label']['handle']!='thermomix' and re.match(".*thermomix",recipes[i]['comment'])==None and len(recipes[i]['ingredients'])>minIngredientAmount):
                    #     recipesFiltred.append(recipes[i])
                    if (any(recipes[i]['ingredients']) and 
                    (recipes[i]['label'] is None or recipes[i]['label']['handle'] != 'thermomix') and 
                    (recipes[i]['comment'] is None or re.match(".*thermomix", recipes[i]['comment']) is None) and 
                    len(recipes[i]['ingredients']) > minIngredientAmount):
                        recipesFiltred.append(recipes[i])
                    else:
                        recipesOutsourced.append(recipes[i])
                except Exception as e:
                    if(recipes[i]['label']==None and len(recipes[i]['ingredients'])>minIngredientAmount):
                        recipesFiltred.append(recipes[i])
                    else:
                        recipesOutsourced.append(recipes[i])

            # recipesFiltred = recipesOutsourced
                        
            print(">> Found ",str(len(recipesFiltred)),"relevant recipes")
            
            # Build final dict container
            print(">> Build final dict container")
            recipesFinal=[]
            ingredients=[]
            ingredients_img=[]
            steps=[]
            steps_img=[]
            tags=[]
            label=[]
            headline=[]
            for i in range(len(recipesFiltred)):
                for j in range(len(recipesFiltred[i]['ingredients'])):
                    ingredient=str(recipesFiltred[i]['ingredients'][j]['name'])
                    try:
                        ingredients_img="https://img.hellofresh.com/c_fit,f_auto,fl_lossy,h_100,q_auto,w_auto/hellofresh_s3" + str(recipesFiltred[i]['ingredients'][j]['imagePath'])
                    except:
                        ingredients_img=""
                    amount=str(recipesFiltred[i]['yields'][0]['ingredients'][j]['amount'])
                    unit=str(recipesFiltred[i]['yields'][0]['ingredients'][j]['unit'])

                    if unit == 'nach Geschmack' or unit == 'None' or unit == 'Einheit':
                        unit = ''
                    if amount == 'None':
                        amount = ''

                    ingredients.append([amount,unit,ingredient,ingredients_img])
                for k in range(len(recipesFiltred[i]['steps'])):
                    step=recipesFiltred[i]['steps'][k]['instructions']
                    try:
                        steps_img="https://img.hellofresh.com/c_fit,f_auto,fl_lossy,h_400,q_auto,w_auto/hellofresh_s3" + str(recipesFiltred[i]['steps'][k]['images'][0]['path'])
                    except:
                        steps_img=""
                    steps.append([step,steps_img])       
                for item in recipesFiltred[i]['tags']:
                    tags.append(item['name'])
                    
                try:
                    label.append(recipesFiltred[i]['label']['text'])
                except:
                    label.append("")
                
                if recipesFiltred[i]['headline'] != None:  
                    try:
                        headline.append(recipesFiltred[i]['headline'])
                    except:
                        headline.append("")
                else:
                    headline.append("")

                
                recipesFinal.append([
                    recipesFiltred[i]['name'],
                    ingredients,
                    '',#recipesFiltred[i]['websiteUrl'],
                    steps,
                    "https://img.hellofresh.com/c_fit,f_auto,fl_lossy,h_1100,q_auto,w_2600/hellofresh_s3"+recipesFiltred[i]['imagePath'],
                    tags,
                    label,
                    headline,
                    recipesFiltred[i].get('id','no_uid') if recipesFiltred[i].get('id','no_uid') != None else 'no_uid'
                    ])
                ingredients=[]
                steps=[]
                tags=[]
                label=[]
                headline=[]
                
            recipes=[]
            recipes=recipesFinal
            
            if saveFiles:
                ''' SQlite connection ------------------------------------------ '''
                ''' convert recipes to single lists '''
                listRecipes = list(map(list, zip(*recipesFinal)))
                
                ''' create SQlite db file '''
                conn = sqlite3.connect('static/db/recipe.db')
                
    
                conn.execute('DROP TABLE IF EXISTS RECIPE;')
                conn.execute('DROP TABLE IF EXISTS INGREDIENTS;')
                conn.execute('DROP TABLE IF EXISTS INSTRUCTIONS;')
                conn.execute('DROP TABLE IF EXISTS TAGS;')
                conn.execute('DROP TABLE IF EXISTS UINGREDIENT;')
                
                conn.execute('''CREATE TABLE RECIPE
                             (ID INT PRIMARY KEY NOT NULL,
                             RECIPE_NAME TEXT NOT NULL,
                             RECIPE_LINK TEXT NOT NULL,
                             RECIPE_SUBTITLE TEXT NOT NULL,
                             RECIPE_LABEL TEXT NOT NULL,
                             RECIPE_IMG TEXT NOT NULL,
                             RECIPE_UID TEXT NOT NULL
                             )
                             ;''')
                conn.execute('''CREATE TABLE INGREDIENTS
                             (ID INT PRIMARY KEY NOT NULL,
                             UID INT NOT NULL,
                             AMOUNT REAL NOT NULL,
                             UNIT TEXT NOT NULL,
                             INGREDIENT TEXT NOT NULL,
                             IMG TEXT NOT NULL
                             )
                             ;''')
                conn.execute('''CREATE TABLE INSTRUCTIONS
                             (ID INT PRIMARY KEY NOT NULL,
                             UID INT NOT NULL,
                             INSTRUCTION TEXT NOT NULL,
                             IMG TEXT NOT NULL
                             )
                             ;''')
                conn.execute('''CREATE TABLE TAGS
                             (ID INT PRIMARY KEY NOT NULL,
                             UID INT NOT NULL,
                             TAG TEXT NOT NULL
                             )
                             ;''')
                cnt = [0,0,0]
                for i in range(len(listRecipes[0])):
                    conn.execute("INSERT INTO RECIPE (ID,RECIPE_NAME,RECIPE_LINK,RECIPE_SUBTITLE,RECIPE_LABEL,RECIPE_IMG,RECIPE_UID) VALUES (?,?,?,?,?,?,?)",
                                 (i,
                                  listRecipes[0][i],
                                  listRecipes[2][i],
                                  listRecipes[7][i][0],
                                  listRecipes[6][i][0],
                                  listRecipes[4][i],
                                  listRecipes[8][i]
                                  ));
                    for j,ingredient in enumerate(listRecipes[1][i]):
                        conn.execute("INSERT INTO INGREDIENTS (ID,UID,AMOUNT,UNIT,INGREDIENT,IMG) VALUES (?,?,?,?,?,?)",(cnt[0],i,ingredient[0],ingredient[1],ingredient[2],ingredient[3]))
                        cnt[0] = cnt[0] + 1
                    for j,instruction in enumerate(listRecipes[3][i]):
                        conn.execute("INSERT INTO INSTRUCTIONS (ID,UID,INSTRUCTION,IMG) VALUES (?,?,?,?)",(cnt[1],i,instruction[0],instruction[1]))
                        cnt[1] = cnt[1] + 1
                    for j,tag in enumerate(listRecipes[5][i]):
                        conn.execute("INSERT INTO TAGS (ID,UID,TAG) VALUES (?,?,?)",(cnt[2],i,tag))
                        cnt[2] = cnt[2] + 1
                    if listRecipes[6][i][0]:
                        conn.execute("INSERT INTO TAGS (ID,UID,TAG) VALUES (?,?,?)",(cnt[2],i,listRecipes[6][i][0]))
                        cnt[2] = cnt[2] + 1
                        
                ''' '''
                conn.execute("CREATE TABLE UINGREDIENT AS SELECT DISTINCT INGREDIENT FROM INGREDIENTS ORDER BY INGREDIENT")
                
                
                ''' Get ingredient conversion table but only results which should be converted '''
                conn_cv = sqlite3.connect('static/db/ingredients.db')
                conversions = conn_cv.execute("SELECT * FROM 'ingredients' WHERE Converted is not '' order by Converted").fetchall()
                conn_cv.close()
                
                for element in conversions:
                    conn.execute("UPDATE INGREDIENTS SET INGREDIENT = REPLACE(INGREDIENT,?,?) WHERE INGREDIENT = ?;",(element[0],element[1],element[0],))
                conn.commit()
                conn.close()
            
            self._isRunning = False


# run = Thread()
# run.run()
