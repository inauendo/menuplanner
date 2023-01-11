import configparser
import re
import random
from os import scandir, remove

def helper(stringarray):
    res = ''
    for entry in stringarray:
        res += entry
        res += " "
    return res[:-1]


class Recipe:

    def __init__(self):
        self.name = ""
        self.flavors = []
        self.ingredients = []
        self.nutrition = 0.0
        self.preptime = 0.0
        self.filepath = ""

    def read(self, filepath):
        '''read a text file containing recipe information'''
        config = configparser.ConfigParser()
        config.read(filepath)
        sectionname = config.sections()[0]  #read out the first section name
        section = config[sectionname]

        #edit recipe object with data from file
        self.filepath = filepath
        self.name = section.get('name', fallback='unnamed recipe')
        self.nutrition = section.getfloat('nutritional value', fallback=0.0)
        self.preptime = section.getfloat('preparation time', fallback=0.0)
        self.flavors = re.split("\W+", section.get('flavors', fallback=""))
        self.ingredients = re.split("\W+", section.get('ingredients', fallback=""))

    def write(self, filepath):
        '''write the recipe into a textfile at the given filepath'''
        config = configparser.ConfigParser()
        config['RECIPE'] = {'name': self.name, 'flavors': helper(self.flavors), 'ingredients': helper(self.ingredients), 'nutritional value': str(self.nutrition), 'preparation time': str(self.preptime)}
        with open(filepath, 'w') as configfile:
            config.write(configfile)

    def print(self, verbose=False):
        '''print the recipe to console'''
        print("name:", self.name)
        print("estimated preparation time:", self.preptime)
        if verbose == True:
            print("main flavors:", self.flavors)
            print("main ingredients:", self.ingredients)
            print("estimated nutritional value:", self.nutrition)

    def clear(self):
        '''removes the recipe file found at self.filepath'''
        remove(self.filepath)

class Menuplan:

    def __init__(self):
        self.recipes = []                       #list of available recipes

        self.configfilepath = 'C:/Users/domin/Desktop/menuplan/config.txt'      #path to config file
        self.recipedir  = 'C:/Users/domin/Desktop/menuplan/recipes'             #path to directory containing recipes

        #lots of constraints for the generation procedure, set to trivial value and read in from config file
        self.days = 5                           #number of days to generate
        self.meals_per_day = 2                  #number of meals in a day
        self.ingredient_repetition = 1          #for how many meals ingredients should not be repeated after one was had
        self.special_ing_rep = {}               #dictionary containing special ingredient restrictions. For example, if 'rice' should not be repeated for three meals, special_ing_rep['rice'] returns 3.
        self.flavor_repetition = 0              #basically the same thing for flavors
        self.special_flav_rep = {}

        self.meals = [Recipe() for j in range(self.meals_per_day*self.days)]    #list of planned meals
        

    def read(self, recipepath, configpath):
        '''read in config data, constraints on generation of menuplan and recipes'''
        
        #read in from configfile
        config = configparser.ConfigParser()
        config.read(configpath)
        general = config['GENERAL']
        self.days = general.getint('days', fallback=5)
        self.ingredient_repetition = general.getint('standard ingredient repetition threshold', fallback=1)
        self.flavor_repetition = general.getint('standard flavor repetition threshold', fallback=0)
        self.special_ing_rep = config['INGREDIENT EXCEPTIONS']
        self.special_flav_rep = config['FLAVOR EXCEPTIONS']

        #read in recipes
        self.recipes = []
        for file in scandir(recipepath):
            tmp = Recipe()
            tmp.read(file.path)
            self.recipes.append(tmp)


    def generate(self, verbose=False):
        '''generate the menuplan, semi-randomly according to set constraints'''

        #get recipes
        self.read(recipepath=self.recipedir, configpath=self.configfilepath)

        for i in range(self.meals_per_day*self.days):
            if self.meals[i].name != "":
                continue

            #find all available recipes
            pool = [recipe for recipe in self.recipes if self.condition(recipe, i)==True]
            if len(pool) < 1:
                raise ValueError('No available recipes under these conditions. Try relaxing some constraints.')

            #choose randomly from pool of available recipes
            self.meals[i] = random.choice(pool)

        if verbose == True:
            print("meal plan generated!\n")
            self.print(verbose=True)

    def condition(self, recipe: Recipe, i):
        '''helper function for the generation of the menuplan. Returns True if recipe is a viable candidate for the recipe with index i, False otherwise.'''
        #if we consider the first meal, return True immediately
        if i == 0:
            return True

        #check whether ingredients in recipe are present in the meal before
        for ing in recipe.ingredients:
            ing_range = int(self.special_ing_rep.get(ing, self.ingredient_repetition))  #the 'range' over which ingredients of meals already selected need to be checked. check in special_ing_rep if there is a special repetition threshold for this ingredient, otherwise use the standard value in ingredient_repetition
            if ing_range == 0:
                continue
            for meal in self.meals[max(0, i-ing_range):min(self.days*self.meals_per_day, i+ing_range+1)]:    #check if in the meals surrounding the newly to be placed, if there are 'problematic' ingredients already
                for ingredient in meal.ingredients:
                    if ingredient == ing:
                        return False

        #check whether flavors in recipe are present in the meal before
        for flav in recipe.flavors:
            flav_range = int(self.special_flav_rep.get(flav, self.flavor_repetition))
            if flav_range == 0:
                continue
            for meal in self.meals[max(0,i-flav_range):min(self.days*self.meals_per_day, i+flav_range+1)]:    #check in special_flav_rep if there is a special repetition threshold for this flavor, otherwise use the standard value in flavor_repetition which is probably 0.
                for flavor in meal.flavors:
                    if flavor == flav:
                        return False

        #generally, we accept all recipes
        return True


    def print(self, verbose=False):
        '''prints the generated menuplan'''
        #todo: make this prettier
        for i in range(self.days):
            print("DAY " + str(i+1) + ":")
            for j in range(self.meals_per_day):
                print("meal " + str(j+1) + ":")
                self.meals[i*self.meals_per_day + j].print(verbose)
                
            print("")

if __name__ == '__main__':
    print(helper(['asd', 'asdf']))
