'''
Created on 21.05.2022

@author: n00b
'''
from lib.Scrape_Weeklys import scrapeWeeklys

class wr_scrapeWeeklys(object):
    '''
    
    == Wrapper class for connecting the individual layers with each other ==
    == Connection between App (Flask) // ScrapeWeeklys ==
    
    '''


    def __init__(self, credentials):
        ''' scrape weeklys from HF '''
        self.class_obj = scrapeWeeklys()
        self.class_obj.login(credentials=credentials)
        self.class_obj.account()
        self.class_obj.weeklys()
        self.results = self.class_obj.stream['WEEKLYS']['meals']
        
    def get(self):
        ''' create array in terms of seperate recipes '''
        array_recipes_sep = [[dic['recipe'].get('name'),
                              dic['recipe'].get('headline'),
                              dic['recipe'].get('image'),
                              dic['recipe']['tags'][0].get('name'),
                              dic.get('recipe').get('label').get('text') if dic.get('recipe').get('label') else ''
                              ] for dic in self.results]
        ''' unzip array in terms of combined to types'''
        return(list(zip(*array_recipes_sep)))