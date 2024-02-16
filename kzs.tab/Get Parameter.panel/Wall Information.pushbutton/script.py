# -*- coding: utf-8 -*-
__title__ = 'Wall Information'
__doc__   ="""This is a simple tool to pick an wall and 
print out some simple information about it."""



# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

# Regular + Autodesk
from Autodesk.Revit.DB import *
from pyrevit import forms, revit
import sys

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# =================================================

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIN
# =================================================

# pyRevit Input
# selected_views = forms.select_views()
# if selected_views:
#     print(selected_views)

# PICK ELEMENT
with forms.WarningBar(title='Pick an Element:'):
    element = revit.pick_element()

element_type = type(element)

if element_type != Wall:
    forms.alert('You were supposed to pick a Wall.', exitscript=True)
    # sys.exit() #import sys

print(element)
print(element_type)

# GET INFORMATION
e_cat       = element.Category.Name
e_id        = element.Id
e_level_id  = doc.GetElement(element.LevelId)
e_wall_type = element.WallType
e_width     = element.Width


print('Element Category: {}'.format(e_cat))
print('ElementId: {}'.format(e_id))
print('ElementLevelId: {}'.format(e_level_id.Name ))
print('Wall WallType:{}'.format(e_wall_type))
print('Wall Width: {}'.format(e_width))