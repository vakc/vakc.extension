# -*- coding: utf-8 -*-
__title__ = 'Create Element'
__doc__   ="""This is a test of RevitAPI about
Creating/Deleting/Copying Elements."""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

# Regular + Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType

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

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIN
# =================================================

with Transaction(doc,__title__) as t :

    t.Start()

    # ╔╦╗╔═╗═╗ ╦╔╦╗╔╗╔╔═╗╔╦╗╔═╗
    #  ║ ║╣ ╔╩╦╝ ║ ║║║║ ║ ║ ║╣
    #  ╩ ╚═╝╩ ╚═ ╩ ╝╚╝╚═╝ ╩ ╚═╝  TEXTNOTE
    # =================================================

    # # ARGUMENTS
    # text_type_id = FilteredElementCollector(doc).OfClass(TextNoteType).FirstElementId()
    # pt = XYZ(0,0,0)
    # text = 'Hello BIM World!'
    # # CREATE TEXT NOTE
    # TextNote.Create(doc, active_view.Id, pt, text, text_type_id)

    # ╦═╗╔═╗╔═╗╔╦╗
    # ╠╦╝║ ║║ ║║║║
    # ╩╚═╚═╝╚═╝╩ ╩  ROOM
    # =================================================

    # ARGUMENTS
    # pt = UV(10,0)
    #
    # # CREATE ROOM
    # room = doc.Create.NewRoom(active_level, pt)
    #
    # # CREATE ROOM TAG
    # room_linkId = LinkElementId(room.Id)
    # New_Room_tag = doc.Create.NewRoomTag(room_linkId, pt, active_view.Id)

    # ╦  ╦╔╗╔╔═╗╔═╗
    # ║  ║║║║║╣ ╚═╗
    # ╩═╝╩╝╚╝╚═╝╚═╝  DETAIL LINES
    # =================================================

    # pt_start = XYZ(20,0,0)
    # pt_end   = XYZ(20,5,0)
    # curve    = Line.CreateBound(pt_start, pt_end)
    #
    # detail_line = doc.Create.NewDetailCurve(active_view, curve)

    # ╦ ╦╔═╗╦  ╦  ╔═╗
    # ║║║╠═╣║  ║  ╚═╗
    # ╚╩╝╩ ╩╩═╝╩═╝╚═╝  WALLS
    # =================================================

    # pt_start = XYZ(30,0,0)
    # pt_end   = XYZ(30,5,0)
    # curve    = Line.CreateBound(pt_start, pt_end)
    #
    # wall = Wall.Create(doc, curve, active_level.Id, False)

    # ╦ ╦╦╔╗╔╔╦╗╔═╗╦ ╦╔═╗
    # ║║║║║║║ ║║║ ║║║║╚═╗
    # ╚╩╝╩╝╚╝═╩╝╚═╝╚╩╝╚═╝  WINDOWS
    # =================================================

    # # ARGUMENTS
    # pt_start = XYZ(30,0,0)
    # pt_end   = XYZ(30,5,0)
    # pt_mid   = (pt_start + pt_end) / 2
    # window_type = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsElementType().FirstElement()
    # # CREATE A WINDOW
    # window = doc.Create.NewFamilyInstance(pt_mid, window_type, wall, StructuralType.NonStructural)

    # ╔═╗╔═╗╔╦╗╦╦ ╦ ╦  ╦╔╗╔╔═╗╔╦╗╔═╗╔╗╔╔═╗╔═╗
    # ╠╣ ╠═╣║║║║║ ╚╦╝  ║║║║╚═╗ ║ ╠═╣║║║║  ║╣
    # ╚  ╩ ╩╩ ╩╩╩═╝╩   ╩╝╚╝╚═╝ ╩ ╩ ╩╝╚╝╚═╝╚═╝
    # =================================================

    # EXTRA FUNCTION
    def get_type_by_name(type_name):
        """Extra Function to get Family Type by name."""
        # CREATE RULE
        param_type = ElementId(BuiltInParameter.ALL_MODEL_TYPE_NAME)
        f_param = ParameterValueProvider(param_type)
        evaluator = FilterStringEquals()
        f_rule = FilterStringRule(f_param, evaluator, type_name)

        # CREATE FILTER
        filter_type_name = ElementParameterFilter(f_rule)

        # GET ELEMENTS
        return FilteredElementCollector(doc).WherePasses(filter_type_name).WhereElementIsElementType().FirstElement()

    # ARGUMENTS
    pt = XYZ(40,0,0)
    symbol = get_type_by_name("1525 x 762mm")

    # CREATE AN ELEMENT
    element = doc.Create.NewFamilyInstance(pt, symbol, StructuralType.NonStructural)










    t.Commit()























