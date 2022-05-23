'''
Created on 22.05.2022

@author: n00b
'''
import scipy.io
import numpy as np

class scrapeDatabase(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''


    def get(self,LOCALE_IDX):
        
        FILENAME_DATA = "data_pkg.mat"
        FILENAME_INGREDIENTS = "ingredients.mat"
        FOLDER_LOCALE = ["db/de-DE/", "db/de-DE-s/", "db/en-US/"]
        
        matFile = scipy.io.loadmat(FOLDER_LOCALE[LOCALE_IDX] + FILENAME_DATA)
        AllIngredients = scipy.io.loadmat(FOLDER_LOCALE[LOCALE_IDX] + FILENAME_INGREDIENTS)['ingredientListUniqueType']
      
        Name = list(list(zip(*matFile['recipes']))[0])
        Name = list(list(zip(*Name))[0])
        
        Ingredients = list(list(zip(*matFile['recipes']))[1])
        for i in range(len(Ingredients)):
            Ingredients[i] = [[item.strip() for item in s] for s in Ingredients[i]]
            Ingredients[i] = [[item.replace("None", "") for item in s] for s in Ingredients[i]]
        
        Link = list(list(zip(*matFile['recipes']))[2])
        Link = list(list(zip(*Link))[0])
        
        Manual = list(list(zip(*matFile['recipes']))[3])
        
        Image = list(list(zip(*matFile['recipes']))[4])
        Image = list(list(zip(*Image))[0])
        
        Tags = list(list(zip(*matFile['recipes']))[5])
        Tags = [[item.strip() for item in s] for s in Tags]
        
        Labels = list(list(zip(*matFile['recipes']))[6])
        for i in range(len(Labels)):
            if not Labels[i]:
                Labels[i] = np.array([""])
        Labels = list(list(zip(*Labels))[0])
        
        Headline = list(list(zip(*matFile['recipes']))[7])
        for i in range(len(Headline)):
            if not Headline[i]:
                Headline[i] = np.array([""])
        Headline = list(list(zip(*Headline))[0])
    
        return([Name, Ingredients, Link, Manual, Image, AllIngredients, Tags, Labels, Headline])

# lrd = loadRecipeDatabase()
# result = lrd.get(0)
# pass