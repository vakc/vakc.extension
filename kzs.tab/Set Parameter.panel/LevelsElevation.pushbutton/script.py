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
Author: vakc"""
# Button Description shown in Revit UI
__author__ = 'vakc'
__helpurl__= "https://www.youtube.com/"
# __highlight__ = 'new'
__min_revit_ver__ = 2022
__max_revit_ver__ = 2024
# __context__ = ['Walls','Floors', 'Roofs'] # Make your button avaiable only when certain categories are selected


# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

# Regular + Autodesk
import os, sys, math, datetime, time
from Autodesk.Revit.DB import * # Import everything from DB (Very good for beginners and development)
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector

# pyRevit
from pyrevit import revit, forms

# Custom Imports
from Snippets._selection import get_selected_elements
from Snippets._convert import convert_internal_to_m

# .NET Imports
import clr
clr.AddReference("System")
from System.Collections.Generic import List # List<ElementType>() <- it's special type of list that RevitAPI often requires.


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# =================================================

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
PATH_SCRIPT = os.path.dirname(__file__)

symbol_start = "【"
symbol_end   = "】"
mode         = 'add'
position     = 'prefix'
# example      = "【+12.69】OG.01 - FBOK"


# from pyrevit.revit import uidoc, doc, app # Alternative

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝  FUNCTIONS
# =================================================
def get_text_in_brackets(text, symbol_start, symbol_end):
    #type:(str,str,str) -> str
    """Function to get content between 2 symbols
    :param text:           Initial Text
    :param symbol_start:   Start Symbol
    :param symbol_end:     End Symbol
    :return:               Text between 2 symbols, if found.
    e.g. get_text_in_brackets('This is [not] very important messages.', '[', ']') -> 'not'"""
    if symbol_start in text and symbol_end in text:
        start = text.find(symbol_start) + len(symbol_start)
        stop  = text.find(symbol_end)
        return text[start:stop]
    return ""


# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝  CLASSES
# =================================================




# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIN
# =================================================

# Get all Levels
all_levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

t = Transaction(doc, __title__)
t.Start()

# Get Levels Elevations + Convert to meters
for lvl in all_levels:
    lvl_elevation = lvl.Elevation
    # lvl_elevation_m = lvl_elevation / 0.3048
    lvl_elevation_m = round(convert_internal_to_m(lvl_elevation),2)
    lvl_elevation_m_str = "+" + str(lvl_elevation_m) if lvl_elevation > 0 else str(lvl_elevation_m)

    # if lvl.Elevation > 0:
    #     var = '+' + str(lvl_elevation_m)
    # else:
    #     var = str(lvl_elevation_m)

    # ELEVATION EXISTS (update)
    if symbol_start in lvl.Name and symbol_end in lvl.Name:
        current_value = get_text_in_brackets(lvl.Name, symbol_start, symbol_end)
        new_name = lvl.Name.replace(current_value, lvl_elevation_m_str)

    # ELEVATION DOES NOT EXIST (new)
    else:
        elevation_value = symbol_start + lvl_elevation_m_str + symbol_end
        new_name = lvl.Name + elevation_value

    # Add/Update Levels Elevation
    try:
        if lvl.Name != new_name:
            current_name = lvl.Name
            lvl.Name = new_name
            print('Remaned: {} -> {}'.format(lvl.Name, new_name))
    except:
        print("Could not change Level's name...")

t.Commit()

print('-'*50)
print('Script is finished. Type keyboard emoji in comments if you managed to follow it until here.')








