# -*- coding: utf-8 -*-
__title__ = 'Copy Elements'
__doc__   ="""This is a test of RevitAPI about
Creating/Deleting/Copying Elements."""


# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

# Regular + Autodesk
from Autodesk.Revit.DB import *
from pyrevit.forms import select_views

#.NET IMPORTS
import clr
clr.AddReference('System')
from System.Collections.Generic import List



# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# =================================================

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application


# ╔═╗╔═╗╔═╗╦ ╦  ╦ ╦╦╔╦╗╦ ╦  ╦  ╦╔═╗╔═╗╔╦╗╔═╗╦═╗
# ║  ║ ║╠═╝╚╦╝  ║║║║ ║ ╠═╣  ╚╗╔╝║╣ ║   ║ ║ ║╠╦╝
# ╚═╝╚═╝╩   ╩   ╚╩╝╩ ╩ ╩ ╩   ╚╝ ╚═╝╚═╝ ╩ ╚═╝╩╚═  COPY WITH VECTOR
# =========================================================================

# wallsToCopy = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElementIds()
# vector = XYZ(50,0,0)
#
# t = Transaction(doc, __title__)
#
# t.Start()
# ElementTransformUtils.CopyElements(doc, wallsToCopy, vector)
# t.Commit()



# ╔═╗╔═╗╔═╗╦ ╦  ╔╗ ╔═╗╔╦╗╦ ╦╔═╗╔═╗╔╗╔  ╦  ╦╦╔═╗╦ ╦╔═╗
# ║  ║ ║╠═╝╚╦╝  ╠╩╗║╣  ║ ║║║║╣ ║╣ ║║║  ╚╗╔╝║║╣ ║║║╚═╗
# ╚═╝╚═╝╩   ╩   ╚═╝╚═╝ ╩ ╚╩╝╚═╝╚═╝╝╚╝   ╚╝ ╩╚═╝╚╩╝╚═╝  COPY BETWEEN VIEWS
# =========================================================================

# TextToCopy = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TextNotes).WhereElementIsNotElementType().ToElements()
#
#
# for Text in TextToCopy:
#     if Text.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM).AsValueString() == 'Text: 2.25mm Trebuchet MS':
#         TextToCopy_Final = Text
#
# TextToCopy_Final_Ilist = List[ElementId]()
# TextToCopy_Final_Ilist.Add(TextToCopy_Final.Id)
#
#
# src_view = doc.ActiveView
# dest_view = select_views(__title__ , multiple=False)
#
# transform = Transform.Identity
# opts = CopyPasteOptions()
#
#
# t = Transaction(doc, __title__)
#
# t.Start()
#
# ElementTransformUtils.CopyElements(src_view, TextToCopy_Final_Ilist, dest_view, transform, opts)
#
# t.Commit()


# ╔═╗╔═╗╔═╗╦ ╦  ╔╗ ╔═╗╔╦╗╦ ╦╔═╗╔═╗╔╗╔  ╔═╗╦═╗╔═╗ ╦╔═╗╔═╗╔╦╗╔═╗
# ║  ║ ║╠═╝╚╦╝  ╠╩╗║╣  ║ ║║║║╣ ║╣ ║║║  ╠═╝╠╦╝║ ║ ║║╣ ║   ║ ╚═╗
# ╚═╝╚═╝╩   ╩   ╚═╝╚═╝ ╩ ╚╩╝╚═╝╚═╝╝╚╝  ╩  ╩╚═╚═╝╚╝╚═╝╚═╝ ╩ ╚═╝  COPY BETWEEN PROJECTS
# ===============================================================================================













