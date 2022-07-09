from lib.Scrape_Weeklys import scrapeWeeklys
        
class hellofresh(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.hellofresh = scrapeWeeklys()
        
    def login(self, username, password):
        return(self.hellofresh.login([username,password]))

    def repeat(self):
        pass
        