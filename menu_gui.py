from menu import *
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import configparser

class Menuplan_window(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Menuplan Generator')
        self.main_layout = QVBoxLayout()
        self.selec_layout = QGridLayout()
        self.button_layout = QHBoxLayout()

        self.plan = Menuplan()

        #configure selection grid
        self.refresh_selectors()

        self.gen_button = QPushButton('GENERATE')
        self.cle_button = QPushButton('clear')
        self.opt_button = QPushButton('options...')
        self.lib_button = QPushButton('recipe library...')

        self.gen_button.clicked.connect(self.generate)
        self.cle_button.clicked.connect(self.clear_selection)
        self.opt_button.clicked.connect(self.launch_options)
        self.lib_button.clicked.connect(self.launch_library)

        self.button_layout.addWidget(self.gen_button, stretch=2)
        self.button_layout.addWidget(self.cle_button)
        self.button_layout.addWidget(self.opt_button)
        self.button_layout.addWidget(self.lib_button)

        self.main_layout.addLayout(self.selec_layout)
        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)

    def refresh_selectors(self):
        '''read in settings from config file and available recipes from recipe folder. Then add these to possible options for the dropdown boxes.'''
        self.plan.read(self.plan.recipedir, self.plan.configfilepath)
        self.selector_list = [QComboBox() for i in range(self.plan.meals_per_day*self.plan.days)]

        for i in reversed(range(self.selec_layout.count())): 
            self.selec_layout.itemAt(i).widget().setParent(None)

        for i in range(self.plan.meals_per_day):
            for j in range(self.plan.days):
                index = j*self.plan.meals_per_day + i
                for item in self.plan.recipes:
                    self.selector_list[index].addItem(item.name)
                self.selector_list[index].addItem("")
                self.selector_list[index].setCurrentText("")
                self.selec_layout.addWidget(self.selector_list[index], i, j)

    def generate(self):
        '''functionality for the generate button, reads the selections made in the selector grid and creates a menuplan to fill the gaps.'''
        self.plan.read(self.plan.recipedir, self.plan.configfilepath)
        self.plan.meals = [Recipe() for j in range(self.plan.meals_per_day*self.plan.days)]
        selected_ind = [i for i in range(len(self.selector_list)) if self.selector_list[i].currentText() != ""]
        for index in selected_ind:
            self.plan.meals[index] = [rec for rec in self.plan.recipes if rec.name == self.selector_list[index].currentText()][0]
        try:
            self.plan.generate()
        except ValueError as err:
            QMessageBox.about(self, 'Error', str(err))
        for i in range(len(self.plan.meals)):
            self.selector_list[i].setCurrentText(self.plan.meals[i].name)

        return 0

    def clear_selection(self):
        '''functionality for the clear button, sets all selection boxes in the grid to an empty string.'''
        for selector in self.selector_list:
            selector.setCurrentText("")
        return 0

    def launch_library(self):
        '''launches the library window'''
        self.lib = Library_window(menu=self.plan)
        self.lib.exit_button.clicked.connect(self.refresh_selectors)
        self.lib.closeSignal.connect(self.refresh_selectors)
        self.lib.show()

    def launch_options(self):
        '''launches the settings window'''
        self.options = Config_window(menu=self.plan)
        self.options.ok_button.clicked.connect(self.refresh_selectors)
        self.options.show()
        

class Library_window(QWidget):
    '''Class for the library window'''

    closeSignal = pyqtSignal()  #signal to emit when library window is closed

    def __init__(self, menu):
        super().__init__()
        self.plan = menu    #copy the menuplan object from the main window
        self.setWindowTitle('Recipe Library')

        #layouts
        self.library_layout = QVBoxLayout()
        self.upper_layout = QGridLayout()
        self.lower_layout = QHBoxLayout()

        #upper layout
        self.refresh()

        #lower layout
        self.new_button = QPushButton('Add new recipe')
        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(self.close)
        self.new_button.clicked.connect(self.new_recipe_func)

        self.lower_layout.addWidget(self.new_button)
        self.lower_layout.addWidget(self.exit_button)

        self.library_layout.addLayout(self.upper_layout)
        self.library_layout.addLayout(self.lower_layout)
        self.setLayout(self.library_layout)

    def refresh(self):
        '''gets the recipe list from the menuplan and lists the recipes'''
        self.plan.read(self.plan.recipedir, self.plan.configfilepath)   #refresh recipes
        self.entrylist = [(recipe, QPushButton('edit'), QPushButton('remove')) for recipe in self.plan.recipes]

        for i in reversed(range(self.upper_layout.count())): 
            self.upper_layout.itemAt(i).widget().setParent(None)

        for i in range(len(self.entrylist)):
            textwidget = QLabel()
            textwidget.setText(self.entrylist[i][0].name)
            edit_button = QPushButton('edit')
            edit_button.clicked.connect(lambda state, index=i: self.edit_recipe_func(self.entrylist[index][0]))
            rem_button = QPushButton('remove')
            rem_button.clicked.connect(self.entrylist[i][0].clear)
            rem_button.clicked.connect(self.refresh)
            self.upper_layout.addWidget(textwidget, i, 0)
            self.upper_layout.addWidget(edit_button, i, 1)
            self.upper_layout.addWidget(rem_button, i, 2)
        

    def closeEvent(self, event):
        '''overload closeEvent such that the closing signal is emitted when the window is closed'''
        self.closeSignal.emit()
        event.accept()

    def edit_recipe_func(self, rec):
        '''functionaly for the edit recipe buttons, opens a Recipe dialog window.'''
        self.editor = Recipe_dialog(recipedir=self.plan.recipedir)
        self.editor.namebox.setText(rec.name)
        flavorstr = ''
        for i in range(len(rec.flavors)):
            flavorstr += rec.flavors[i]
            if i != len(rec.flavors)-1:
                flavorstr += ", "
        ingredientstr = ''
        for i in range(len(rec.ingredients)):
            ingredientstr += rec.ingredients[i]
            if i != len(rec.ingredients)-1:
                ingredientstr += ", "
        
        self.editor.flavorbox.setText(flavorstr)
        self.editor.ingredientbox.setText(ingredientstr)
        self.editor.preptimebox.setValue(int(rec.preptime))
        self.editor.nutritionbox.setValue(int(rec.nutrition))
        self.editor.ok_button.clicked.connect(self.new_rec_accepted)
        self.editor.show()

    def rem_recipe_func(self, index):
        '''functionality for the remove recipe buttons. index is the recipe's index in the menuplan recipe list'''
        self.entrylist[index][0].clear()
        self.refresh()

    def new_recipe_func(self):
        '''functionality for the new recipe button'''
        self.editor = Recipe_dialog(recipedir=self.plan.recipedir)
        self.editor.ok_button.clicked.connect(self.new_rec_accepted)
        self.editor.show()

    def new_rec_accepted(self):
        '''functionality for the "OK" button in the recipe dialog window. Refreshes the menuplan object (background) and the recipe library window.'''
        self.plan.read(self.plan.recipedir, self.plan.configfilepath)
        self.refresh()


class Recipe_dialog(QWidget):
    '''Window for editing and viewing recipes in the recipe library.'''
    def __init__(self, recipedir = ''):
        super().__init__()
        self.recipedir = recipedir
        self.setWindowTitle('Recipe Editor')

        self.upper_layout = QFormLayout()
        self.namebox = QLineEdit()
        self.flavorbox = QLineEdit()
        self.ingredientbox = QLineEdit()
        self.preptimebox = QSpinBox()
        self.nutritionbox = QSpinBox()
        self.upper_layout.addRow('Name:', self.namebox)
        self.upper_layout.addRow('Flavors:', self.flavorbox)
        self.upper_layout.addRow('Main ingredients:', self.ingredientbox)
        self.upper_layout.addRow('Preparation time:', self.preptimebox)
        self.upper_layout.addRow('Nutritional value:', self.nutritionbox)

        self.lower_layout = QHBoxLayout()
        self.ok_button = QPushButton('OK')
        self.cancel_button = QPushButton('cancel')
        self.cancel_button.clicked.connect(self.close)
        self.ok_button.clicked.connect(self.ok_button_func)
        self.lower_layout.addWidget(self.ok_button)
        self.lower_layout.addWidget(self.cancel_button)

        self.window_layout = QVBoxLayout()
        self.window_layout.addLayout(self.upper_layout)
        self.window_layout.addLayout(self.lower_layout)
        self.setLayout(self.window_layout)

    def ok_button_func(self):
        '''functionality for the "OK" button. Writes a new text file to the recipe directory with the settings entered in the window.'''
        config = configparser.ConfigParser()
        config['RECIPE'] = {'name': self.namebox.text(), 'flavors': self.flavorbox.text(), 'ingredients': self.ingredientbox.text(), 'nutritional value': self.nutritionbox.value(), 'preparation time': self.preptimebox.value()}
        with open(self.recipedir+"/"+self.namebox.text()+".txt", 'w') as configfile:
            config.write(configfile)
        self.close()

class Config_window(QWidget):
    '''Class for the settings window.'''
    def __init__(self, menu):
        super().__init__()
        self.plan = menu
        self.setWindowTitle('Options')

        #lists of exceptions
        self.ing_exp_list = [[QLabel('Avoid'), QLineEdit(), QLabel('for'), QSpinBox(), QLabel('meals.'), QPushButton('remove'), key] for key in self.plan.special_ing_rep]
        self.ing_flav_list = [[QLabel('Avoid'), QLineEdit(), QLabel('for'), QSpinBox(), QLabel('meals.'), QPushButton('remove'), key] for key in self.plan.special_flav_rep]


        #initialize layouts
        self.window_layout = QVBoxLayout()
        self.upper_layout = QGridLayout()
        self.middle_layout = QVBoxLayout()
        self.middler_layout = QVBoxLayout()
        self.lower_layout = QHBoxLayout()        

        #edit upper layout
        days_text = QLabel('Amount of days:')
        st_ing_rep_thre_text = QLabel('Meals for which ingredients are not repeated:')
        st_flav_rep_thre_text = QLabel('Meals for which flavors are not repeated:')
        self.days_box = QSpinBox()
        self.st_ing_rep_thre_box = QSpinBox()
        self.st_flav_rep_thre_box = QSpinBox()

        self.days_box.setValue(self.plan.days)
        self.st_ing_rep_thre_box.setValue(self.plan.ingredient_repetition)
        self.st_flav_rep_thre_box.setValue(self.plan.flavor_repetition)

        self.upper_layout.addWidget(days_text, 0, 0)
        self.upper_layout.addWidget(self.days_box, 0, 1)
        self.upper_layout.addWidget(st_ing_rep_thre_text, 1, 0)
        self.upper_layout.addWidget(self.st_ing_rep_thre_box, 1, 1)
        self.upper_layout.addWidget(st_flav_rep_thre_text, 2, 0)
        self.upper_layout.addWidget(self.st_flav_rep_thre_box, 2, 1)

        self.draw_exceptions()

        #edit lower layout
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton('cancel')
        self.cancel_button.clicked.connect(self.close)

        self.lower_layout.addWidget(self.ok_button)
        self.lower_layout.addWidget(self.cancel_button)

        #merge layouts
        self.upper_box = QGroupBox('Standard thresholds')
        self.upper_box.setLayout(self.upper_layout)

        self.middle_box = QGroupBox('Ingredient exceptions')
        self.middle_box.setLayout(self.middle_layout)

        self.middler_box = QGroupBox('Flavor exceptions')
        self.middler_box.setLayout(self.middler_layout)


        self.window_layout.addWidget(self.upper_box)
        self.window_layout.addWidget(self.middle_box)
        self.window_layout.addWidget(self.middler_box)
        self.window_layout.addLayout(self.lower_layout)
        self.setLayout(self.window_layout)

    def draw_exceptions(self):
        '''edit the layout containing flavor and ingredient exceptions'''
        #edit middle layout
        self.temp_layout_ing = QGridLayout()
        j=0
        for row in self.ing_exp_list:
            for i in range(len(row)-1):
                row[1].setText(row[-1])
                row[3].setValue(int(self.plan.special_ing_rep[row[-1]]))
                row[5].clicked.connect(lambda state, index=j: self.remove_exception_ing(index))
                self.temp_layout_ing.addWidget(row[i], j, i)
            j += 1
        
        self.middle_layout.addLayout(self.temp_layout_ing)
        self.new_exception_button = QPushButton('Add new exception')
        self.new_exception_button.clicked.connect(self.add_new_ing_exp)
        self.middle_layout.addWidget(self.new_exception_button)

        #edit middler layout
        self.temp_layout_flav = QGridLayout()
        j=0
        for row in self.ing_flav_list:
            for i in range(len(row)-1):
                row[1].setText(row[-1])
                row[3].setValue(int(self.plan.special_flav_rep[row[-1]]))
                row[5].clicked.connect(lambda state, index=j: self.remove_exception_flav(index))
                self.temp_layout_flav.addWidget(row[i], j, i)
            j += 1
        
        self.middler_layout.addLayout(self.temp_layout_flav)
        self.new_exception_button_two = QPushButton('Add new exception')
        self.new_exception_button_two.clicked.connect(self.add_new_flav_exp)
        self.middler_layout.addWidget(self.new_exception_button_two)


    def add_new_ing_exp(self):
        '''functionality for the "Add new exception" button in the settings window, under ingredients. Adds a new line for a new ingredient exception.'''
        new_index = self.temp_layout_ing.rowCount()
        for entry in [QLabel('Avoid'), QLineEdit(), QLabel('for'), QSpinBox(), QLabel('meals.')]:
            self.temp_layout_ing.addWidget(entry)
        rem_button = QPushButton('remove')
        rem_button.clicked.connect(lambda state, index=new_index: self.remove_exception_ing(index))
        self.temp_layout_ing.addWidget(rem_button)

    def add_new_flav_exp(self):
        '''functionality for the "Add new exception" button in the settings window, under flavors. Adds a new line for a new flavor exception.'''
        new_index = self.temp_layout_flav.rowCount()
        for entry in [QLabel('Avoid'), QLineEdit(), QLabel('for'), QSpinBox(), QLabel('meals.')]:
            self.temp_layout_flav.addWidget(entry)
        rem_button = QPushButton('remove')
        rem_button.clicked.connect(lambda state, index=new_index: self.remove_exception_flav(index))
        self.temp_layout_flav.addWidget(rem_button)

    def remove_exception_ing(self, index):
        '''functionality for the "remove" button of ingredient exceptions.'''
        for j in range(5, -1, -1):
            self.temp_layout_ing.itemAtPosition(index, j).widget().deleteLater()

    def remove_exception_flav(self, index):
        '''functionality for the "remove" button of flavor exceptions.'''
        for j in range(5, -1, -1):
            self.temp_layout_flav.itemAtPosition(index, j).widget().deleteLater()

    def accept(self):
        '''functionality for the "OK" button in the settings window. Edits the config file with the options entered in the settings window.'''
        config = configparser.ConfigParser()
        config['GENERAL'] = {'days': self.days_box.value(), 'standard ingredient repetition threshold': str(self.st_ing_rep_thre_box.value()), 'standard flavor repetition threshold': str(self.st_flav_rep_thre_box.value())}
        ing_dict = {}
        flav_dict = {}
        for i in range(self.temp_layout_ing.rowCount()):
            try:
                ing_dict[self.temp_layout_ing.itemAtPosition(i, 1).widget().text()] = self.temp_layout_ing.itemAtPosition(i, 3).widget().value()
            except AttributeError:
                continue
        for i in range(self.temp_layout_flav.rowCount()):
            try:
                flav_dict[self.temp_layout_flav.itemAtPosition(i, 1).widget().text()] = self.temp_layout_flav.itemAtPosition(i, 3).widget().value()
            except AttributeError:
                continue
        config['INGREDIENT EXCEPTIONS'] = ing_dict
        config['FLAVOR EXCEPTIONS'] = flav_dict

        with open(self.plan.configfilepath, 'w') as configfile: 
            config.write(configfile)

        self.close()
            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wind = Menuplan_window()
    wind.show()
    sys.exit(app.exec())