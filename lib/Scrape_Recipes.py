import sys
import os
import requests
import re
import urllib.request
import time
import numpy as np
import base64
from scipy.io import savemat, loadmat
from tqdm import tqdm
from PyQt5.QtCore import QThread, pyqtSignal

host = "https://gw.hellofresh.com"
salt = "hellofresh-ios-customer:ca154f43-687b-4866-9d4e-a618f42da8c9"

class TQDM:
    def __init__(self,r):
        self.tq=tqdm(r)
    
    def remaining(self):
        rate = self.tq.format_dict["rate"]
        remaining = (self.tq.total - self.tq.n) / rate if rate and self.tq.total else 0  # Seconds*        
        remaining = time.strftime('%H:%M:%S', time.gmtime(remaining))
        return remaining    

class Thread(QThread):
    _signal = pyqtSignal(int)
    _state_msg = pyqtSignal('QString')
    _max = pyqtSignal(int)
    def __init__(self):
        super(Thread, self).__init__()
        self._isRunning = True

    def __del__(self):
        self.wait()
        
    def stop(self):
        self._isRunning = False
        
    def auth(self):
        url = f"{host}/auth/token?locale=de-DE&country=DE"
        payload = "grant_type=client_credentials&scope=public"
        headers = {
          'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
          'authorization': f'Basic {str(base64.b64encode(salt.encode("ascii")), "utf-8")}'
        }
        return(requests.request("POST", url, headers=headers, data=payload).json()['access_token'])

    def run(self):
        
        # run thread while flag is True
        while self._isRunning:
            # create new session
            session = requests.Session()
            
            # HelloFresh URL
            url = f"{host}/api/recipes/search?"
            
            # maximum items to return are 250
            limit = 250
            # take only recipes in consideration if there ingredient amount is more than 3
            minIngredientAmount = 3
            # Should also are the images saved?
            saveImg=True
            buildCorMatrix=True
            
            LOCALE=["de-DE","en-US"]
            COUNTRY=["de","us"]
            
            locale=LOCALE[0]
            country=COUNTRY[0]
            
            payload={
              "offset": "0",
              "limit": str(limit),
              "locale": locale,
              "country": country
            }
            
            self._state_msg.emit("Get fresh bearer auth token...")
            # apply bearer
            headers = {
              'Authorization': f"Bearer {self.auth()}"
              }
            
            # find out how many recipes are present (only german DE market)
            response = requests.get(url, headers=headers, params=payload).json()
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
            _tqdmObj = TQDM(range(iterations))
            for i in _tqdmObj.tq:
                if not self._isRunning:
                    break
                self._max.emit(iterations)
                self._signal.emit(i)
                self._state_msg.emit("Step 1/8\n\nDownload "+str(i)+" of "+str(iterations)+" packages server\n\nRemaining Time "+_tqdmObj.remaining())
                payload={
                    "offset": str(offset),
                    "limit": str(limit),
                    "locale": locale,
                    "country": country
                }
                offset += 250
                recipes.extend(session.request("GET", url, headers=headers, params=payload).json()['items'])
            
            # Drop recipes when
            # - ingredients list is empty
            # - thermomix classified
            # - ingredients amount less than "minIngredientAmount"
            recipesFiltred=[]
            recipesOutsourced=[]
            for i in range(total):
                if not self._isRunning:
                    break
                try:
                    if(any(recipes[i]['ingredients']) and recipes[i]['label']['handle']!='thermomix' and re.match(".*thermomix",recipes[i]['comment'])==None and len(recipes[i]['ingredients'])>minIngredientAmount):
                        recipesFiltred.append(recipes[i])
                    else:
                        recipesOutsourced.append(recipes[i])
                except:
                    if(recipes[i]['label']==None and len(recipes[i]['ingredients'])>minIngredientAmount):
                        recipesFiltred.append(recipes[i])
                    else:
                        recipesOutsourced.append(recipes[i])
                        
            print(">> Found ",str(len(recipesFiltred)),"relevant recipes")
            
            # Build final dict container
            print(">> Build final dict container")
            recipesFinal=[]
            ingredients=[]
            steps=[]
            tags=[]
            label=[]
            headline=[]
            for i in range(len(recipesFiltred)):
                for j in range(len(recipesFiltred[i]['ingredients'])):
                    ingredient=str(recipesFiltred[i]['ingredients'][j]['name'])
                    amount=str(recipesFiltred[i]['yields'][0]['ingredients'][j]['amount'])
                    unit=str(recipesFiltred[i]['yields'][0]['ingredients'][j]['unit'])
                    ingredients.append([amount,unit,ingredient])
                for k in range(len(recipesFiltred[i]['steps'])):
                    steps.append(recipesFiltred[i]['steps'][k]['instructionsMarkdown'])
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

                
                recipesFinal.append([recipesFiltred[i]['name'],ingredients,recipesFiltred[i]['websiteUrl'],steps,"https://img.hellofresh.com/c_fit,f_auto,fl_lossy,h_1100,q_auto,w_2600/hellofresh_s3"+recipesFiltred[i]['imagePath'],tags,label,headline])
                ingredients=[]
                steps=[]
                tags=[]
                label=[]
                headline=[]
                
            recipes=[]
            recipes=recipesFinal
            
            
            if country=="de":
                ite=2
            else:
                ite=1
            # Loop for simplify the recipes
            # (1) standard
            # (2) simple
            for opt in range(ite):
                if not self._isRunning:
                    break
                if opt==0:
                    print(">> Start standard recipe session")
                    self._max.emit(ite)
                    self._signal.emit(0)
                    self._state_msg.emit("Start standard recipe session")
                else:
                    print(">> Start simplified recipe session")
                print(">> Create ingredient list")
                Ingredients = []
                tmp=[]
                matFile=loadmat('db/de-DE-s/dict.mat')['HelloIngredients'][1:]
                _tqdmObj = TQDM(range(len(recipes)))
                for i in _tqdmObj.tq:
                    self._max.emit(len(recipes))
                    self._signal.emit(i)
                    if opt:
                        step="6"
                    else:
                        step="2"
                    self._state_msg.emit("Step "+step+"/8\n\nRearrange the recipes...\n\nRemaining Time "+_tqdmObj.remaining())
                    if not self._isRunning:
                        break
                    for j in range(len(recipes[i][1])):
                        # Should be simplified?
                        if(opt):
                            for k in range(len(matFile)):
                                if matFile[k][0][0].strip()==recipes[i][1][j][2]:
                                    if matFile[k][1]:
                                        recipes[i][1][j][2]=matFile[k][1][0].strip()
                            tmp.append(recipes[i][1][j][2])
                        else:
                            tmp.append(recipes[i][1][j][2])
                    Ingredients.append(tmp)
                    tmp=[]
                    
                # Save image urls to file
                if(saveImg and not opt):
                    print(">> Load and save recipe images")
                    _tqdmObj = TQDM(range(len(recipes)))
                    for i in _tqdmObj.tq:
                        if not self._isRunning:
                            break
                        self._max.emit(len(recipes))
                        self._signal.emit(i)
                        self._state_msg.emit("Step 3/8\n\nDownload recipe image "+str(i)+" of "+str(len(recipes))+"\n\nRemaining Time "+_tqdmObj.remaining())
                        try:
                            urllib.request.urlretrieve(recipes[i][4], "img/"+locale+"/"+str(i)+".jpg")
                        except:
                            urllib.request.urlretrieve("https://help.ifttt.com/hc/article_attachments/360041394694/no_image_card.png", "img/"+locale+"/"+str(i)+".jpg")
                
                # Build ingredient recipes correlation matrix
                if(buildCorMatrix):
                    print(">> Build correlation matrix")
                    s_CrlFct = np.zeros([len(Ingredients),len(Ingredients)])
                    _tqdmObj = TQDM(range(len(Ingredients)))
                    for j in _tqdmObj.tq:
                        if not self._isRunning:
                            break
                        self._max.emit(len(Ingredients))
                        self._signal.emit(j)
                        if opt:
                            step="7"
                        else:
                            step="4"
                        self._state_msg.emit("Step "+step+"/8\n\nBuild correlation matrix...\n\nRemaining Time "+_tqdmObj.remaining())
                        for k in range(len(Ingredients)):
                            ar = Ingredients[j] + Ingredients[k]
                            s_NotUnique = len(ar)
                            s_Unique = len(np.unique(ar))
                            s_CrlFct[j][k] = abs(s_Unique - s_NotUnique)
                    
                    
                
                # Build unique ingredient list
                print(">> Create final unique ingredient list")
                ingredientListUniqueType=[]
                _tqdmObj = TQDM(range(len(Ingredients)))
                for j in _tqdmObj.tq:
                    self._max.emit(len(Ingredients))
                    self._signal.emit(j)
                    if opt:
                        step="8"
                    else:
                        step="5"
                    self._state_msg.emit("Step "+step+"/8\n\nSave all results...")
                    for k in range(len(Ingredients[j])):
                        ingredientListUniqueType.append(Ingredients[j][k])
                ingredientListUniqueType=np.unique(ingredientListUniqueType)
                
                if self._isRunning:
                    if(opt):
                        # Path to simplified data
                        path="db/"+locale+"-s/"
                    else:
                        # Standard path
                        path="db/"+locale+"/"
                    if(buildCorMatrix):
                        # Save the correlation matrix to *.mat file
                        savemat(path+"cor_fac.mat", {"CorrelationFactors":s_CrlFct})
                    # Save the ingredient list to *.mat file
                    savemat(path+"ingredients.mat", {"ingredientListUniqueType":ingredientListUniqueType})
                    # Save the recipes to *.mat file
                    savemat(path+"data_pkg.mat", {"recipes":recipes})
                    
            
            self._isRunning = False
            
            for i in (range(5)):
                time.sleep(1)
                self._state_msg.emit("Update finished\n\nApp will be restarted in "+str(4-i)+"...")
                
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)


t=Thread()
t.run()
