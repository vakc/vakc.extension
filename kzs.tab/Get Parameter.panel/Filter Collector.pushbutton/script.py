# -*- coding: utf-8 -*-
__title__ = 'Filter Collector'
__doc__   ="""This is a test of RevitAPI Filter Collector about 
how to work with them."""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

import clr
clr.AddReference('System')
from System.Collections.Generic import List

# Regular + Autodesk
from Autodesk.Revit.DB import *
from pyrevit import forms, revit

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# =================================================

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

active_view = doc.ActiveView

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIN
# =================================================

all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).ToElements()
all_elements = FilteredElementCollector(doc).OfClass(Wall).WhereElementIsNotElementType().ToElements()

all_doors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
all_windows = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()

all_views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
all_legend = [view for view in all_views if view.ViewType == ViewType.Legend]

all_col_in_view = (FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements())

# print(all_rooms)
# print(all_elements)

categories = List[BuiltInCategory]([BuiltInCategory.OST_Columns,
                                    BuiltInCategory.OST_Walls,
                                    BuiltInCategory.OST_Doors,
                                    BuiltInCategory.OST_Windows])

custom_filter = ElementMulticategoryFilter(categories)
my_element = FilteredElementCollector(doc).WherePasses(custom_filter).WhereElementIsNotElementType().ToElements()

print(my_element)



