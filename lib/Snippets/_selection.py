#  -*- coding: utf-8 -*-

# IMPORTS
from Autodesk.Revit.DB import *

# VARIABLES
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document
# FUNCTIONS

def get_selected_elements(uidoc):
    selected_elements = []

    for elem_id in uidoc.Selection.GetElementIds():
        elem = uidoc.Document.GetElement(elem_id)
        selected_elements.append(elem)
    return selected_elements