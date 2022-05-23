'''
Created on 21.05.2022

@author: n00b
'''
from lib.Scrape_Database import scrapeDatabase

class wr_scrapeDatabase(object):
    '''
    
    == Wrapper class for connecting the individual layers with each other ==
    == Connection between App (Flask) // ScrapeWeeklys ==
    
    '''


    def __init__(self):
        ''' scrape from database '''
        self.class_obj = scrapeDatabase()
        self.retval = self.class_obj.get(0)
        
    def get(self):
        
        num = []
        for i in range(len(self.retval[6])):
            if not self.retval[6][i]:
                self.retval[6][i] = [""]
            num.append("static/images/de-DE/" + str(i) + ".jpg")
        
        ''' create array in terms of seperate recipes '''
        retval = [self.retval[0],
                  self.retval[8],
                  num,
                  list(list(zip(*self.retval[6]))[0]),
                  self.retval[7]
                  ]
        ''' unzip array in terms of combined to types'''
        return(retval)
    
    
# obj = wr_scrapeDatabase()
# r = obj.get()
# pass