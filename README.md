# Menuplan

This is a personal project to generate weekly mealplans for myself. The code selects recipes stored as .txt files in the /recipes directory according to rules defined in config.txt. Rules are available to avoid repetition of certain flavors or ingredients for a given number of days. For example, a rule can be defined to avoid recipes containing fish for 4 meals after one has been selected. Although fields for preparation time and nutritional value are prepared in the recipe files, there is currently no functionality for these fields to influence the meal plan.

menu.py contains all necessary background functionality. menu_gui.py contains the GUI and is the recommended way of using the meal planner. Via the GUI, the recipe library can be accessed and edited easily. The 'options' button allows for customization of the meal planner rules.
