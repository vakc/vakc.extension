# -*- coding: utf-8 -*-
__title__ = 'Add Levels Elevation' # Name of the button displayed in Revit UI
__doc__   = """Version = 1.0
Date      = 11.01.2024
_______________________________________________________________________________________________
Description:

This tool will add/update yor level name to have its elevation.
_______________________________________________________________________________________________
How-to:

-> Click on the button
-> Change Settings(optional)
-> Rename Levels
_______________________________________________________________________________________________
Last update:
- [11.01.2024] - 1.0 RELEASE
_______________________________________________________________________________________________
To-Do:
_______________________________________________________________________________________________
Author: vakc
"""# Button Description shown in Revit UI
__author__ = 'vakc'
__helpurl__= "https://www.youtube.com/"
__highlight__ = 'new'
__min_revit_ver__ = 2019
__max_revit_ver__ = 2022
__context__ = ['Walls','Floors', 'Roofs'] # Make your button avaiable only when certain categories are selected

# IMPORTS

# Regular + Autodesk
import os, sys, math, datetime, time
from Autodesk.Revit.DB import * # Import everything from DB (Very good for beginners and development)
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector

# pyRevit
from pyrevit import revit, forms

# Custom Imports
from Snippets._selection import get_selected_elements

# .NET Imports
import clr
clr.AddReference("System")
from System.Collections.Generic import List # List<ElementType>() <- it's special type of list that RevitAPI often requires.

# VARIABLES
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
PATH_SCRIPT = os.path.dirname(__file__)

# from pyrevit.revit import uidoc, doc, app # Alternative


