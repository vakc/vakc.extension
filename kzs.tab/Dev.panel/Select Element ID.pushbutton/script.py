#  -*- coding: utf-8 -*-


__title__  =  "Select ElementID"
__author__ =  "vakc"
__doc__    =  """This will show the elementID selected.
Click on it to see what happens..."""

# VARIABLES
uidoc = __revit__.ActiveUIDocument

# CUSTOM IMPORT
from Snippets._selection import get_selected_elements

if  __name__  == '__main__':
    print(get_selected_elements(uidoc))